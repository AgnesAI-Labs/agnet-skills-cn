#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历文本提取工具 — 多格式容错提取（PDF / Word docx / TXT / MD）

- PDF：pypdf -> pdfplumber -> pdfminer.six -> pypdfium2 四级引擎降级，并清洗水印噪声
- docx：python-docx 提取段落与表格
- txt / md：自动探测编码（utf-8 / utf-8-sig / gbk / gb18030 / latin-1）
- 其他：明确报错，不做静默失败
- 内置候选人姓名启发式识别

跨平台支持：Windows / macOS / Linux

依赖安装（按需，至少满足目标格式）：
  pip install pypdf                    # PDF，推荐，纯 Python 轻量级
  pip install pdfplumber               # PDF，保留布局
  pip install pdfminer.six             # PDF，解析最彻底
  pip install pypdfium2                # PDF，Chromium 内核，处理非常规 PDF
  pip install python-docx              # Word docx

用法：
  # 提取单个简历（控制台输出摘要）
  python extract_resume_text.py <文件路径>

  # 输出机器可读 JSON（含全文、文件名、类型、引擎、页数、识别到的姓名）
  python extract_resume_text.py <文件路径> --json

  # 控制台直接查看完整文本
  python extract_resume_text.py <文件路径> --detail

  # 提取并保存为 txt
  python extract_resume_text.py <文件路径> -o 输出.txt

  # 批量提取目录下所有简历
  python extract_resume_text.py <目录路径> --batch -o <输出目录>

  # 指定 PDF 首选引擎 / 关闭水印清洗
  python extract_resume_text.py <文件路径> --engine pdfplumber
  python extract_resume_text.py <文件路径> --no-clean --detail

  # 环境检测与能力清单
  python extract_resume_text.py --check
  python extract_resume_text.py --list-engines

在代码中导入：
  import sys
  sys.path.append("scripts 目录路径")
  from extract_resume_text import extract_resume

  result = extract_resume("path/to/简历.pdf")
  if result["success"]:
      text = result["text"]
      name = result["candidate_name"]
  else:
      print(result["error"])
"""

import argparse
import glob
import json
import os
import platform
import re
import sys

# 文本文件候选编码，按优先级探测
TEXT_ENCODINGS = ["utf-8", "utf-8-sig", "gbk", "gb18030", "latin-1"]

# 支持的文件扩展名
PDF_EXTS = [".pdf"]
DOCX_EXTS = [".docx"]
TEXT_EXTS = [".txt", ".md"]
SUPPORTED_EXTS = PDF_EXTS + DOCX_EXTS + TEXT_EXTS

# 不支持但简历中常见的扩展名，需给出明确指引
KNOWN_UNSUPPORTED_EXTS = [".doc", ".rtf", ".odt", ".wps", ".pages"]


# ============================================================================
# 跨平台编码修复
# ============================================================================
def _fix_encoding():
    """
    确保 stdout/stderr 使用 UTF-8 输出，兼容 Python 3.6+ 全平台。
    """
    if sys.getdefaultencoding() == "utf-8" and getattr(
        sys.stdout, "encoding", ""
    ).lower() in ("utf-8", "utf8"):
        return  # 已是 UTF-8

    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
            return
    except Exception:
        pass

    try:
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
    except Exception:
        os.environ.setdefault("PYTHONIOENCODING", "utf-8")


_fix_encoding()


# ============================================================================
# PDF 引擎注册（import 失败静默降级）
# ============================================================================
PDF_ENGINES = []

try:
    import pypdf

    def _pdf_pypdf(filepath: str) -> str:
        texts = []
        reader = pypdf.PdfReader(filepath)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                texts.append(t)
        return "\n".join(texts)

    PDF_ENGINES.append(("pypdf", _pdf_pypdf))
except ImportError:
    pass

try:
    import pdfplumber

    def _pdf_pdfplumber(filepath: str) -> str:
        texts = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    texts.append(t)
        return "\n".join(texts)

    PDF_ENGINES.append(("pdfplumber", _pdf_pdfplumber))
except ImportError:
    pass

try:
    from pdfminer.high_level import extract_text as _pdfminer_extract

    def _pdf_pdfminer(filepath: str) -> str:
        return _pdfminer_extract(filepath) or ""

    PDF_ENGINES.append(("pdfminer.six", _pdf_pdfminer))
except ImportError:
    pass

try:
    import pypdfium2 as pdfium

    def _pdf_pypdfium2(filepath: str) -> str:
        texts = []
        pdf = pdfium.PdfDocument(filepath)
        for page in pdf:
            textpage = page.get_textpage()
            t = textpage.get_text_bounded()
            if t:
                texts.append(t)
            textpage.close()
        pdf.close()
        return "\n".join(texts)

    PDF_ENGINES.append(("pypdfium2", _pdf_pypdfium2))
except ImportError:
    pass


# ============================================================================
# docx 引擎注册
# ============================================================================
try:
    import docx as _python_docx

    def _docx_extract(filepath: str) -> str:
        document = _python_docx.Document(filepath)
        parts = []

        # 段落
        for para in document.paragraphs:
            if para.text.strip():
                parts.append(para.text.strip())

        # 表格（简历中常用于基本信息栏）
        for idx, table in enumerate(document.tables, 1):
            rows_text = []
            for row in table.rows:
                cells = [c.text.strip() for c in row.cells]
                if any(cells):
                    rows_text.append(" | ".join(cells))
            if rows_text:
                parts.append(f"[表格{idx}]")
                parts.extend(rows_text)

        # 页眉页脚（部分模板把姓名放在页眉）
        for section in document.sections:
            for container in (section.header, section.footer):
                for para in container.paragraphs:
                    if para.text.strip():
                        parts.append(para.text.strip())

        return "\n".join(parts)

    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


# ============================================================================
# 纯文本读取
# ============================================================================
def _read_plain_text(filepath: str):
    """按候选编码依次尝试读取纯文本，返回 (文本, 实际编码)"""
    for enc in TEXT_ENCODINGS:
        try:
            with open(filepath, "r", encoding=enc) as f:
                return f.read(), enc
        except (UnicodeDecodeError, LookupError):
            continue
        except OSError as e:
            return None, str(e)

    # 全部编码失败时，以 latin-1 强制解码，保证不丢内容
    try:
        with open(filepath, "r", encoding="latin-1", errors="replace") as f:
            return f.read(), "latin-1(replace)"
    except OSError as e:
        return None, str(e)


# ============================================================================
# PDF 噪声清洗（仅对 PDF 生效，避免误杀 docx/文本中的正常长行）
# ============================================================================
_NOISE_PATTERN_LINE = re.compile(r"^\s*[a-zA-Z0-9+/=_\-]{40,}\s*$", re.MULTILINE)
_NOISE_PATTERN_LONGLINE = re.compile(r"^\s*\S{100,}\s*$", re.MULTILINE)


def clean_pdf_noise(text: str) -> str:
    """
    清洗 PDF 提取后的水印/噪声。逐行匹配而非全局替换，避免误杀正常业务文本。
    """
    if not text:
        return text
    text = _NOISE_PATTERN_LINE.sub("", text)
    text = _NOISE_PATTERN_LONGLINE.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ============================================================================
# 候选人姓名启发式识别
# ============================================================================
_NAME_LABEL = re.compile(r"姓\s*名\s*[:：]\s*([一-龥·]{2,8})")
_NAME_BARE = re.compile(r"^[一-龥·]{2,4}$")

# 前几行中这些词虽为短中文串，但不是姓名
_NAME_STOPWORDS = {
    "简历", "个人简历", "求职简历", "个人信息", "基本信息", "联系方式",
    "教育背景", "工作经历", "项目经历", "专业技能", "自我评价", "求职意向",
    "应聘岗位", "期望岗位", "个人评价", "求职简历表", "简历表",
}


def guess_candidate_name(text: str, filepath: str) -> str:
    """
    从简历文本中启发式识别候选人姓名。

    返回 (姓名, 置信度)，置信度取值：
      high   —— 命中「姓名：xxx」标签
      medium —— 命中开头处的 2-4 字纯中文行
      low    —— 回退为文件名（不含扩展名）
    """
    lines = [l.strip() for l in (text or "").splitlines()[:10] if l.strip()]

    for line in lines:
        m = _NAME_LABEL.search(line)
        if m:
            return m.group(1), "high"

    for line in lines[:3]:
        if _NAME_BARE.match(line) and line not in _NAME_STOPWORDS:
            return line, "medium"

    return os.path.splitext(os.path.basename(filepath))[0], "low"


# ============================================================================
# 页数探测
# ============================================================================
def _detect_pdf_pages(filepath: str, engine_name: str) -> int:
    try:
        if engine_name == "pypdf":
            import pypdf

            return len(pypdf.PdfReader(filepath).pages)
        if engine_name == "pdfplumber":
            import pdfplumber

            with pdfplumber.open(filepath) as pdf:
                return len(pdf.pages)
        if engine_name == "pdfminer.six":
            from pdfminer.pdfparser import PDFParser
            from pdfminer.pdfdocument import PDFDocument

            with open(filepath, "rb") as f:
                return len(list(PDFDocument(PDFParser(f)).get_pages()))
        if engine_name == "pypdfium2":
            import pypdfium2 as pdfium

            pdf = pdfium.PdfDocument(filepath)
            n = len(pdf)
            pdf.close()
            return n
    except Exception:
        pass
    return 0


# ============================================================================
# 核心提取函数
# ============================================================================
def _empty_result(filepath: str) -> dict:
    ext = os.path.splitext(filepath)[1].lower()
    return {
        "success": False,
        "filepath": os.path.abspath(filepath),
        "filetype": ext.lstrip("."),
        "engine": None,
        "pages": 0,
        "chars": 0,
        "candidate_name": os.path.splitext(os.path.basename(filepath))[0],
        "name_confidence": "low",
        "text": "",
        "error": None,
    }


def _extract_pdf(filepath: str, preferred_engine=None, no_clean=False) -> dict:
    result = _empty_result(filepath)
    result["filetype"] = "pdf"

    if not PDF_ENGINES:
        result["error"] = (
            "没有可用的 PDF 解析引擎。请至少安装一个：\n"
            "  pip install pypdf         # 推荐，纯 Python 轻量级\n"
            "  pip install pdfplumber    # 保留布局\n"
            "  pip install pdfminer.six  # 解析最彻底\n"
            "  pip install pypdfium2     # Chromium 内核"
        )
        return result

    if preferred_engine:
        order = [e for e in PDF_ENGINES if e[0] == preferred_engine]
        order += [e for e in PDF_ENGINES if e[0] != preferred_engine]
    else:
        order = PDF_ENGINES[:]

    last_error = None
    for engine_name, extractor in order:
        try:
            raw = extractor(filepath)
            if raw and raw.strip():
                result["text"] = raw if no_clean else clean_pdf_noise(raw)
                result["pages"] = _detect_pdf_pages(filepath, engine_name)
                result["success"] = True
                result["engine"] = engine_name
                result["chars"] = len(result["text"])
                return result
            last_error = f"引擎 {engine_name} 提取结果为空"
        except Exception as e:
            last_error = f"引擎 {engine_name} 报错: {e}"

    result["error"] = (
        f"所有 PDF 引擎均提取失败（共尝试 {len(order)} 个）。最后错误：{last_error}"
    )
    return result


def _extract_docx(filepath: str) -> dict:
    result = _empty_result(filepath)
    result["filetype"] = "docx"

    if not DOCX_AVAILABLE:
        result["error"] = "未安装 python-docx，无法解析 Word 文档。请执行：pip install python-docx"
        return result

    try:
        text = _docx_extract(filepath)
        if text and text.strip():
            result["text"] = text.strip()
            result["success"] = True
            result["engine"] = "python-docx"
            result["chars"] = len(result["text"])
            return result
        result["error"] = "docx 解析成功但内容为空（可能是纯图片排版的简历）"
    except Exception as e:
        result["error"] = f"docx 解析失败: {e}"
    return result


def _extract_text(filepath: str) -> dict:
    result = _empty_result(filepath)
    result["filetype"] = os.path.splitext(filepath)[1].lstrip(".").lower()

    content, enc = _read_plain_text(filepath)
    if content is None:
        result["error"] = f"文本读取失败: {enc}"
        return result

    if content.strip():
        result["text"] = content.strip()
        result["success"] = True
        result["engine"] = enc
        result["chars"] = len(result["text"])
        return result

    result["error"] = "文件内容为空"
    return result


def extract_resume(filepath: str, preferred_engine: str = None,
                    no_clean: bool = False) -> dict:
    """
    提取简历文本，按扩展名自动分派解析器。

    Args:
        filepath: 简历文件路径
        preferred_engine: PDF 首选引擎名，None 表示按优先级自动选择
        no_clean: True 表示关闭 PDF 水印清洗（仅对 PDF 生效）

    Returns:
        dict: {
            "success": bool,
            "filepath": str,            # 绝对路径
            "filetype": str,            # pdf / docx / txt / md
            "engine": str,              # 实际使用的解析器或编码
            "pages": int,               # 页数（仅 PDF）
            "chars": int,               # 文本字符数
            "candidate_name": str,      # 启发式识别到的候选人姓名
            "name_confidence": str,     # high / medium / low
            "text": str,                # 提取的文本
            "error": str or None,
        }
    """
    if not os.path.isfile(filepath):
        r = _empty_result(filepath)
        r["error"] = f"文件不存在: {filepath}"
        return r

    ext = os.path.splitext(filepath)[1].lower()

    if ext in PDF_EXTS:
        result = _extract_pdf(filepath, preferred_engine, no_clean)
    elif ext in DOCX_EXTS:
        result = _extract_docx(filepath)
    elif ext in TEXT_EXTS:
        result = _extract_text(filepath)
    elif ext in KNOWN_UNSUPPORTED_EXTS:
        result = _empty_result(filepath)
        hint = {
            ".doc": "请用 Word 另存为 .docx",
            ".rtf": "请另存为 .docx 或 .pdf",
            ".odt": "请另存为 .docx 或 .pdf",
            ".wps": "请另存为 .docx 或 .pdf",
            ".pages": "请导出为 .pdf 后再提交",
        }.get(ext, "请转换为 PDF 或 DOCX 后再提交")
        result["error"] = f"暂不支持 {ext} 格式的简历。{hint}。"
    else:
        result = _empty_result(filepath)
        result["error"] = (
            f"不支持的文件类型 {ext or '(无扩展名)'}。"
            f"当前支持：{', '.join(SUPPORTED_EXTS)}"
        )

    if result["success"]:
        name, confidence = guess_candidate_name(result["text"], filepath)
        result["candidate_name"] = name
        result["name_confidence"] = confidence

    return result


# ============================================================================
# 文件查找
# ============================================================================
def find_resume_files(directory: str):
    """查找目录下所有受支持的简历文件（扩展名大小写不敏感）"""
    found = []
    for entry in sorted(os.scandir(directory), key=lambda e: e.name):
        if not entry.is_file():
            continue
        ext = os.path.splitext(entry.name)[1].lower()
        if ext in SUPPORTED_EXTS:
            found.append(entry.path)
    return found


# ============================================================================
# 输出格式化
# ============================================================================
def format_result(result: dict, show_detail: bool = False) -> str:
    """格式化提取结果为可读文本"""
    if not result["success"]:
        return f"[失败] {result['filepath']}\n  原因: {result['error']}"

    meta = f"  类型: {result['filetype']}  |  解析器: {result['engine']}  |  字符数: {result['chars']}"
    if result["filetype"] == "pdf":
        meta += f"  |  页数: {result['pages']}"
    meta += f"  |  姓名: {result['candidate_name']}（置信度 {result['name_confidence']}）"

    lines = [f"[成功] {result['filepath']}", meta]
    if show_detail:
        lines.append("")
        lines.append(result["text"])
    return "\n".join(lines)


def to_json(result: dict) -> str:
    """序列化为机器可读 JSON"""
    return json.dumps(result, ensure_ascii=False, indent=2)


# ============================================================================
# 命令行入口
# ============================================================================
def build_parser():
    available_engines = [e[0] for e in PDF_ENGINES]
    parser = argparse.ArgumentParser(
        description="简历文本提取工具 — 多格式容错提取（PDF / docx / txt / md，跨平台）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("target", nargs="?", default=None,
                        help="简历文件路径，或包含简历的目录（配合 --batch 使用）")
    parser.add_argument("-o", "--output",
                        help="输出文件路径（单文件模式）或输出目录（batch 模式）")
    parser.add_argument("--batch", action="store_true",
                        help="批量模式：提取指定目录下所有受支持的简历文件")
    parser.add_argument("--engine", choices=available_engines or None,
                        help="指定 PDF 首选解析引擎（可用: " + ", ".join(available_engines) + "）")
    parser.add_argument("--detail", action="store_true",
                        help="在控制台输出完整的简历文本")
    parser.add_argument("--json", action="store_true",
                        help="以 JSON 输出提取结果（含全文与识别到的姓名）")
    parser.add_argument("--no-clean", action="store_true",
                        help="不进行 PDF 水印清洗，保留原始提取结果")
    parser.add_argument("--list-engines", action="store_true",
                        help="列出当前环境中可用的解析器")
    parser.add_argument("--check", action="store_true",
                        help="检测当前运行环境与依赖情况")
    return parser


def cmd_list_engines():
    print("当前环境可用的解析器：")
    if PDF_ENGINES:
        for name, _ in PDF_ENGINES:
            print(f"  - PDF 引擎: {name}")
    else:
        print("  - PDF 引擎: (无，请 pip install pypdf)")

    print(f"  - Word docx: {'python-docx 已安装' if DOCX_AVAILABLE else '(未安装，请 pip install python-docx)'}")
    print(f"  - 纯文本   : 内置，无需依赖（支持 {', '.join(TEXT_EXTS)}）")
    print("\n支持的文件类型：" + ", ".join(SUPPORTED_EXTS))
    print(f"系统平台：{platform.platform()}")
    print(f"Python版本：{sys.version.split()[0]}")


def cmd_check():
    print("=" * 56)
    print("简历文本提取工具 - 环境检测报告")
    print("=" * 56)
    print(f"  系统平台:      {platform.platform()}")
    print(f"  Python版本:    {sys.version.split()[0]}")
    print(f"  Python路径:    {sys.executable}")
    print(f"  stdout编码:    {getattr(sys.stdout, 'encoding', 'unknown')}")
    print(f"  stderr编码:    {getattr(sys.stderr, 'encoding', 'unknown')}")
    print(f"  文件系统编码:  {sys.getfilesystemencoding()}")
    print(f"  支持格式:      {', '.join(SUPPORTED_EXTS)}")
    print("-" * 56)
    print(f"  PDF 引擎:      {', '.join(e[0] for e in PDF_ENGINES) if PDF_ENGINES else '(无)'}")
    print(f"  Word docx:     {'已安装' if DOCX_AVAILABLE else '(未安装)'}")
    print(f"  纯文本:        内置")
    print("=" * 56)
    missing = []
    if not PDF_ENGINES:
        missing.append("pypdf")
    if not DOCX_AVAILABLE:
        missing.append("python-docx")
    if missing:
        print("建议补装：" + " ".join(missing))
        print(f"  pip install {' '.join(missing)}")


def cmd_extract(args):
    target = args.target

    # ================= 批量模式 =================
    if args.batch:
        if not os.path.isdir(target):
            print(f"错误：批量模式需要指定目录，但 '{target}' 不是目录", file=sys.stderr)
            sys.exit(1)

        files = find_resume_files(target)
        if not files:
            print(f"目录 '{target}' 中没有受支持的简历文件（支持：{', '.join(SUPPORTED_EXTS)}）")
            return

        output_dir = args.output or target
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        ok, failed = 0, 0
        for fpath in files:
            result = extract_resume(fpath, preferred_engine=args.engine, no_clean=args.no_clean)
            if result["success"]:
                base = os.path.splitext(os.path.basename(fpath))[0]
                outpath = os.path.join(output_dir, f"{base}.txt")
                with open(outpath, "w", encoding="utf-8") as f:
                    f.write(result["text"])
                print(format_result(result))
                print(f"  已保存: {outpath}")
                ok += 1
            else:
                print(format_result(result), file=sys.stderr)
                failed += 1

        print(f"\n批量提取完成：成功 {ok}/{len(files)}，失败 {failed}/{len(files)}，输出目录 {output_dir}")
        return

    # ================= 单文件模式 =================
    if not os.path.isfile(target):
        print(f"错误：'{target}' 不是有效的文件路径", file=sys.stderr)
        sys.exit(1)

    result = extract_resume(target, preferred_engine=args.engine, no_clean=args.no_clean)

    if args.json:
        print(to_json(result))
        if not result["success"]:
            sys.exit(1)
        return

    if args.output:
        if result["success"]:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(result["text"])
            print(format_result(result))
            print(f"  已保存: {args.output}")
        else:
            print(format_result(result), file=sys.stderr)
            sys.exit(1)
    else:
        print(format_result(result, show_detail=args.detail))
        if not result["success"]:
            sys.exit(1)


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.list_engines:
        cmd_list_engines()
        return
    if args.check:
        cmd_check()
        return

    if args.target is None:
        parser.print_help()
        print("\n错误：必须指定目标简历文件或目录（--list-engines / --check 可省略）",
              file=sys.stderr)
        sys.exit(1)

    cmd_extract(args)


if __name__ == "__main__":
    main()
