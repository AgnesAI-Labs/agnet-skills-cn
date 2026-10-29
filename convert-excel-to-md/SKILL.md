---
name: convert-excel-to-md
name_zh: Excel 转 Markdown
description: >-
  Converts Excel (.xlsx) workbooks into Markdown so their contents can be
  accurately analyzed, summarized, searched, or extracted from. Use this skill
  whenever the user shares, references, or asks about a .xlsx file — even if
  they don't say "convert" or "markdown" explicitly. This includes requests to
  "read", "summarize", "review", "extract data from", "compare", "chart", or
  "analyze" a spreadsheet, workbook, budget, data export, or tracker. Always
  run the bundled conversion script to produce Markdown first; do not attempt
  to parse .xlsx content directly or write ad-hoc extraction code. Also use
  this skill for batch requests involving a whole folder of Excel workbooks.
  IMPORTANT: When the user references a folder or set of documents containing
  multiple file types (.pdf, .docx, .xlsx), invoke ALL three sibling skills —
  convert-pdf-to-md, convert-word-to-md, and convert-excel-to-md — so no file
  type is silently skipped.
description_zh: >-
  先把 .xlsx 工作簿转成 Markdown 再处理：读、汇总、比对、取数这类请求都走转换，避免直接猜表格结构。支持一次处理一整个文件夹里的多个表格。
category: data
category_name: Data & Documents
category_name_zh: 文档与数据
examples_zh:
  - 把这个表格转成 markdown
  - 看看这份 xlsx 里有什么
  - 分析一下这个工作簿
examples:
  - Convert this spreadsheet to markdown
  - Summarize this xlsx file
  - Analyze this workbook
author: github
version: '1.0'
tags:
  - excel
  - xlsx
  - markdown
  - conversion
installation_notes: >-
  Needs Python 3 and the dependency in scripts/requirements.txt
  (markitdown[xlsx]); the conversion script ships with the skill.
installation_notes_zh: >-
  需要本机 Python 3 与 scripts/requirements.txt 里的依赖（markitdown[xlsx]），转换脚本已随技能附带。
license: Complete terms in LICENSE.txt
---

# Convert Excel to Markdown

## When to use this skill

Trigger this skill any time there is a `.xlsx` file that needs to be
understood or processed — for example, a user attaches a spreadsheet and
asks questions about it, wants a summary of the data, wants specific rows or
values pulled out, or wants multiple workbooks in a folder processed
together. Excel's native `.xlsx` format is a zipped XML bundle that is not
reliably readable as plain text, so always convert it to Markdown first
using the script in this skill rather than trying to open or parse the file
directly.

This skill only supports `.xlsx`. If asked to convert a legacy `.xls` file,
tell the user it isn't supported and ask them to re-save it as `.xlsx`
(Excel: File > Save As > Excel Workbook (.xlsx)) first.

**Mixed file types:** When the user references a folder or set of documents
containing multiple supported file types (`.pdf`, `.docx`, `.xlsx`), this
skill handles only `.xlsx` files. The agent MUST also invoke the sibling
skills in parallel:
- `convert-pdf-to-md` for any `.pdf` files
- `convert-word-to-md` for any `.docx` files

Never process a folder and silently skip a supported file type. All three
skills must be invoked together when mixed types are present.

## Setup (once per environment)

Before the first conversion in a given environment, follow
[`references/setup.md`](references/setup.md) step by step to ensure Python,
pip, and the `markitdown` package are installed. Do this proactively rather
than guessing whether the environment is ready — the script itself will
also fail with a clear pointer back to that file if `markitdown` turns out
to be missing, so it's safe to just try the conversion first if you're
reasonably confident setup was already done.

## Usage

The conversion script lives at `scripts/convert_excel_to_md.py`.

**Output structure:** MarkItDown's XLSX converter renders each sheet as its
own `## <SheetName>` Markdown table — it has no support for embedded images
at all. This script separately extracts real embedded images (raster
pictures, not charts) and maps them to the sheet they belong to, writing a
self-contained folder per document:

```
<name>/
    img/
        sheet001_<sheetname>_img001.<ext>
        sheet002_<sheetname>_img001.<ext>
        ...
    <name>.md          (each sheet's images appear right after its table,
                         under a "#### Images in this sheet" heading)
```

This is per-sheet placement, not exact cell position — the finest
granularity MarkItDown's stable output anchors (the `## <SheetName>`
headings) allow. If a workbook has no embedded images, no `img/` folder or
image sections are created. Native Excel **charts** are not extracted as
images (only actual embedded pictures are — charts would need to be
rendered by Excel/LibreOffice, which this lightweight skill does not do).

**Single file:**

```powershell
python scripts\convert_excel_to_md.py "C:\path\to\workbook.xlsx"
```

This creates a `workbook\` folder next to the source file (containing
`workbook.md` and, if present, `workbook\img\`). To control the destination
folder explicitly:

```powershell
python scripts\convert_excel_to_md.py "C:\path\to\workbook.xlsx" -o "C:\path\to\output_folder"
```

**A folder of workbooks (batch mode):**

```powershell
python scripts\convert_excel_to_md.py "C:\path\to\folder"
```

Add `--recursive` to also include subfolders:

```powershell
python scripts\convert_excel_to_md.py "C:\path\to\folder" --recursive
```

Each `.xlsx` found gets its own `<name>\` output folder next to it by
default. Pass `-o "C:\path\to\output_parent"` to collect all the generated
`<name>\` folders under a separate parent directory instead (subfolder
structure is preserved when combined with `--recursive`).

After conversion, read the resulting `.md` file(s) to perform the actual
analysis the user asked for — the script's job is only to produce accurate
Markdown (and images), not to interpret the content.

## Deciding where output goes

**Default — always output next to the source file.** The `<name>/` folder
is created in the same directory as the source `.xlsx`. This is the required
default for every case. Do NOT override it unless the user explicitly asks
for a different location.

**Only use `-o` when** the user explicitly provides an output path (e.g.,
"save the output to `C:\output`", "put the results in `D:\work`"). Do NOT
pass `-o` based on the agent's current working directory, the session state
folder, or any implied location.

**If the source file path cannot be fully resolved** — for example, the
user provides only a filename with no directory, or the path is ambiguous —
use `ask_user` to confirm the full absolute path before running the
conversion. Never guess or assume the directory.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'markitdown'` / exit code 2 | MarkItDown not installed | Follow `references/setup.md` |
| `ERROR: Unsupported file type '.xls'` / exit code 3 | Legacy `.xls`, not `.xlsx` | Ask the user to re-save as `.xlsx` |
| `ERROR: Input path not found` / exit code 3 | Wrong path, or file moved | Confirm the correct path with the user |
| `FAILED <file> -> ...` in batch output | That specific file is corrupt, password-protected, or otherwise unreadable | Report which file(s) failed; other files in the batch still succeed |
| `NOTE: skipped N non-.xlsx file(s)` | Folder contains non-Excel files | Expected — those files are intentionally ignored |
| A sheet's charts don't appear as images | Charts are chart objects, not embedded pictures — this skill only extracts real embedded raster images | Expected; mention this limitation if the user specifically needs chart images |
