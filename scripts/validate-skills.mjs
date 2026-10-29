#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

/**
 * CLI
 *  --skills "skill-a,skill-b"      Only validate these skill dirs (changed-skills-only)
 *  --report path/to/report.json    Write a JSON report (CI reads it for the gate and PR comment)
 *
 * Without --skills the whole repo is validated, which is what local runs want.
 */
function parseArgs(argv) {
  const args = { skills: null, report: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--skills") args.skills = (argv[++i] || "").trim();
    else if (a === "--report") args.report = (argv[++i] || "").trim();
  }
  return args;
}

const { skills: skillsArg, report: reportArg } = parseArgs(process.argv.slice(2));

// 只有显式传入 --report 才落盘，避免本地跑一次就在工作区留下未跟踪文件
const EFFECTIVE_REPORT_PATH = reportArg ? path.resolve(reportArg) : null;

const REPO_ROOT = process.cwd();
const SKILLS_ROOT = REPO_ROOT;

const MAX_FILE_BYTES = 1_000_000;
const MAX_FILES_PER_SKILL = 400;

// Binary masquerading sampling (keep fast + predictable)
const TEXT_SAMPLE_MAX_BYTES = 64 * 1024;
const MIN_PRINTABLE_RATIO = 0.8;
// 编码异常按 warning 记入报告，不阻断合并
const UTF8_REPLACEMENT_WARN_RATIO = 0.02;

const DENY_FILENAMES = new Set([
  ".env",
  ".env.local",
  ".env.production",
  ".env.development",
  ".npmrc",
  ".yarnrc",
  ".pypirc",
  "id_rsa",
  "id_ed25519",
  "known_hosts",
  "authorized_keys",
]);

const DENY_EXTENSIONS = new Set([
  ".exe",
  ".dll",
  ".dmg",
  ".pkg",
  ".msi",
  ".bin",
  ".so",
  ".class",
  ".jar",
  ".pyc",
  ".o",
  ".a",
  ".zip",
  ".tar",
  ".gz",
  ".7z",
]);

const ALLOW_EXTENSIONS = new Set([
  ".md",
  ".txt",
  ".json",
  ".yaml",
  ".yml",
  ".toml",
  ".graphql",
  ".css",
  ".html",
  ".svg",
  ".js",
  ".mjs",
  ".cjs",
  ".ts",
  ".tsx",
  ".jsx",
  ".py",
  ".sh",
  ".bash",
  ".zsh",
  // PowerShell 是文本脚本，文档站清单构建已把它算作可执行脚本；
  // 白名单缺这一项会让带 Windows 等价脚本的技能无法入库。
  ".ps1",
  ".sql",
]);

const ALLOW_FILENAMES = new Set([
  "SKILL.md",
  "LICENSE",
  "NOTICE",
  "README",
  "README.md",
  "package.json",
  "package-lock.json",
  "pnpm-lock.yaml",
  "yarn.lock",
  // Bun 的文本锁文件不带扩展名之外的标识，按文件名放行
  "bun.lock",
  ".gitignore",
]);

// 随包的二进制素材：字体、图标、PDF。它们不参与文本采样（字体天然含 NUL 字节），
// 改为校验文件头与扩展名相符——否则把可执行文件或压缩包改名成 .png 就能绕过上面那张表。
// 表里没有的二进制类型一律不放行，新增格式时同时补上签名。
const BINARY_ASSET_SIGNATURES = new Map([
  [".png", [[0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]]],
  [".jpg", [[0xff, 0xd8, 0xff]]],
  [".jpeg", [[0xff, 0xd8, 0xff]]],
  [".gif", [[0x47, 0x49, 0x46, 0x38]]],
  [".ico", [[0x00, 0x00, 0x01, 0x00]]],
  [".pdf", [[0x25, 0x50, 0x44, 0x46]]],
  [".woff", [[0x77, 0x4f, 0x46, 0x46]]],
  [".woff2", [[0x77, 0x4f, 0x46, 0x32]]],
  [
    ".ttf",
    [
      [0x00, 0x01, 0x00, 0x00],
      [0x4f, 0x54, 0x54, 0x4f],
      [0x74, 0x72, 0x75, 0x65],
      [0x74, 0x74, 0x63, 0x66],
    ],
  ],
  [
    ".otf",
    [
      [0x4f, 0x54, 0x54, 0x4f],
      [0x00, 0x01, 0x00, 0x00],
      [0x74, 0x74, 0x63, 0x66],
    ],
  ],
]);

const BINARY_ASSET_EXTENSIONS = new Set(BINARY_ASSET_SIGNATURES.keys());

// Detect "binary pretending to be text" using magic bytes + text-likeness heuristics
const MAGIC = [
  { name: "ELF", bytes: [0x7f, 0x45, 0x4c, 0x46] },
  { name: "PE", bytes: [0x4d, 0x5a] }, // MZ
  { name: "ZIP", bytes: [0x50, 0x4b, 0x03, 0x04] },
  { name: "PDF", bytes: [0x25, 0x50, 0x44, 0x46] }, // %PDF
  { name: "PNG", bytes: [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a] },
  { name: "GZIP", bytes: [0x1f, 0x8b] },
  { name: "WASM", bytes: [0x00, 0x61, 0x73, 0x6d] }, // \0asm
];

function detectMagic(buf) {
  for (const m of MAGIC) {
    if (buf.length >= m.bytes.length && m.bytes.every((b, i) => buf[i] === b)) return m.name;
  }
  return null;
}

function matchesBinaryAssetSignature(ext, buf) {
  const signatures = BINARY_ASSET_SIGNATURES.get(ext);
  if (!signatures) return false;
  return signatures.some((sig) => sig.every((b, i) => buf[i] === b));
}

function analyzeTextlikeness(buf) {
  let nulFound = false;
  for (let i = 0; i < buf.length; i++) {
    if (buf[i] === 0) nulFound = true;
  }

  // \u6309\u89E3\u7801\u540E\u7684\u5B57\u7B26\u7EDF\u8BA1\uFF0C\u800C\u4E0D\u662F\u6309\u5B57\u8282\uFF1A\u4E2D\u6587\u4E00\u4E2A\u5B57\u5360\u4E09\u5B57\u8282\u4E14\u90FD\u843D\u5728 ASCII \u533A\u95F4\u5916\uFF0C
  // \u6309\u5B57\u8282\u7B97\u4F1A\u628A\u6B63\u5E38\u7684\u4E2D\u6587\u6587\u6863\u5224\u6210\u4E8C\u8FDB\u5236\u3002\u63A7\u5236\u5B57\u7B26\u548C\u66FF\u6362\u5B57\u7B26\u624D\u7B97\u4E0D\u53EF\u6253\u5370\u3002
  const text = buf.toString("utf8");
  let printable = 0;
  for (const ch of text) {
    const cp = ch.codePointAt(0);
    const isControl = (cp < 0x20 && cp !== 0x09 && cp !== 0x0a && cp !== 0x0d) || cp === 0x7f;
    if (!isControl && cp !== 0xfffd) printable++;
  }

  const printableRatio = text.length ? printable / text.length : 1;
  const repl = (text.match(/\uFFFD/g) || []).length;
  const replacementRatio = text.length ? repl / text.length : 0;

  return { nulFound, printableRatio, replacementRatio };
}

function readFileSample(absPath, sizeBytes) {
  const sampleSize = Math.min(TEXT_SAMPLE_MAX_BYTES, sizeBytes);
  if (sampleSize <= 0) return Buffer.alloc(0);

  const fd = fs.openSync(absPath, "r");
  try {
    const buf = Buffer.alloc(sampleSize);
    fs.readSync(fd, buf, 0, sampleSize, 0);
    return buf;
  } finally {
    fs.closeSync(fd);
  }
}

// mcp 是插件数据目录（mcp/servers.json），不是技能目录；
// 与 .github/workflows/validate-skills.yml 里 changed-dirs 的忽略规则保持一致
const IGNORE_DIRS_AT_ROOT = new Set([".git", ".github", "scripts", "node_modules", "mcp", "suites", "dist"]);

// 当前正在校验的技能目录，由主循环设置，用于把结论归到 findings 的 skill 字段
let currentSkill = null;

const findings = [];
let failCount = 0;
let warnCount = 0;

function stripSkillPrefix(msg) {
  const prefix = `${currentSkill}: `;
  return msg.startsWith(prefix) ? msg.slice(prefix.length) : msg;
}

function fail(msg) {
  failCount++;
  findings.push({ severity: "FAIL", skill: currentSkill, message: stripSkillPrefix(msg) });
  console.error(`❌ ${msg}`);
}

function warn(msg) {
  warnCount++;
  findings.push({ severity: "WARN", skill: currentSkill, message: stripSkillPrefix(msg) });
  console.warn(`⚠️ ${msg}`);
}

function ok(msg) {
  console.log(`✅ ${msg}`);
}

// 报告结构对齐 .github/workflows/validate-skills.yml 里的骨架，CI 直接读 summary.fail_count
function writeReport(scannedSkills) {
  if (!EFFECTIVE_REPORT_PATH) return;

  const report = {
    scanned_skills: scannedSkills,
    summary: {
      fail_count: failCount,
      warn_count: warnCount,
      status: failCount > 0 ? "FAILED" : warnCount > 0 ? "WARN" : "PASSED",
    },
    findings,
    timestamp: new Date().toISOString(),
  };

  fs.mkdirSync(path.dirname(EFFECTIVE_REPORT_PATH), { recursive: true });
  fs.writeFileSync(EFFECTIVE_REPORT_PATH, JSON.stringify(report, null, 2), "utf8");
  console.log(`📝 Report written to ${EFFECTIVE_REPORT_PATH}`);
}

function isSymlink(p) {
  return fs.lstatSync(p).isSymbolicLink();
}

function safeJoin(base, target) {
  const resolved = path.resolve(base, target);
  if (!resolved.startsWith(path.resolve(base) + path.sep)) {
    throw new Error(`Path traversal detected: ${target}`);
  }
  return resolved;
}

// --- frontmatter parsing ---
// \u53EA\u5B9E\u73B0\u6821\u9A8C\u9700\u8981\u7684 YAML \u5B50\u96C6\uFF1A\u9876\u5C42 key\u3001\u5757\u6807\u91CF\uFF08>/| \u53CA\u5176 +/- \u53D8\u4F53\uFF09\u3001\u5217\u8868\u3001\u5D4C\u5957\u5757\u3002
// \u9047\u5230\u65E0\u6CD5\u8BC6\u522B\u7684\u9876\u5C42\u884C\u4ECD\u7136\u629B\u9519\uFF0C\u4FDD\u6301\u95E8\u7981\u7684\u4E25\u683C\u6027\u3002
function parseFrontmatter(md) {
  const trimmed = md.replace(/^\uFEFF/, "");
  if (!trimmed.startsWith("---\n")) return null;
  const end = trimmed.indexOf("\n---\n", 4);
  if (end === -1) return null;

  const lines = trimmed.slice(4, end).replace(/\r\n?/g, "\n").split("\n");
  const fm = {};

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!line.trim()) continue;

    const kv = line.match(/^([A-Za-z0-9_-]+):(.*)$/);
    if (!kv) throw new Error(`Unsupported frontmatter line: "${line}"`);

    const key = kv[1];
    const value = kv[2].trim();

    if (/^[|>][+-]?$/.test(value)) {
      const block = collectIndentedBlock(lines, i + 1);
      i = block.next - 1;
      fm[key] =
        value[0] === ">"
          ? block.raw.map((l) => l.trim()).join(" ").trim()
          : block.raw.join("\n");
      continue;
    }

    if (value === "") {
      const block = collectIndentedBlock(lines, i + 1);
      i = block.next - 1;
      const contentLines = block.raw.filter((l) => l.trim());
      const listItems = contentLines
        .filter((l) => /^\s*-\s+/.test(l))
        .map((l) => l.replace(/^\s*-\s+/, "").trim());

      // \u5168\u662F\u5217\u8868\u9879\u624D\u7B97\u5217\u8868\uFF1B\u5D4C\u5957\u6620\u5C04\uFF08\u5982 od:\uFF09\u4E0D\u53C2\u4E0E required \u5B57\u6BB5\u6821\u9A8C\uFF0C\u8BB0\u4E3A\u7A7A
      fm[key] = contentLines.length > 0 && listItems.length === contentLines.length ? listItems : "";
      continue;
    }

    fm[key] = value.replace(/^"(.*)"$/, "$1").replace(/^'(.*)'$/, "$1");
  }

  return { frontmatter: fm };
}

// \u6536\u96C6\u6BD4\u5F53\u524D\u884C\u66F4\u7F29\u8FDB\u7684\u5757\u5185\u5BB9\uFF0C\u76F4\u5230\u4E0B\u4E00\u4E2A\u9876\u5C42\u884C\u4E3A\u6B62\uFF1B\u5757\u5185\u7684\u7A7A\u884C\u4E0D\u8868\u793A\u5757\u7ED3\u675F\u3002
function collectIndentedBlock(lines, start) {
  const raw = [];
  let i = start;

  while (i < lines.length) {
    const line = lines[i];
    if (!line.trim()) {
      let j = i + 1;
      while (j < lines.length && !lines[j].trim()) j++;
      if (j >= lines.length || !/^\s/.test(lines[j])) break;
      raw.push("");
      i = j;
      continue;
    }
    if (!/^\s/.test(line)) break;
    raw.push(line);
    i++;
  }

  return { raw, next: i };
}

function validateSkillFrontmatter(skillName, fm) {
  const required = ["name", "description", "author", "version"];
  for (const k of required) {
    const v = fm[k];
    if (typeof v !== "string" || !v.trim()) {
      fail(`${skillName}: frontmatter "${k}" must be a non-empty string`);
    }
  }

  const tags = fm.tags;
  if (
    !Array.isArray(tags) ||
    tags.length === 0 ||
    tags.some((t) => typeof t !== "string" || !t.trim())
  ) {
    fail(`${skillName}: frontmatter "tags" must be a non-empty list of strings`);
  }
}

function walkDir(dir, relativeBase) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  const files = [];

  for (const ent of entries) {
    const rel = path.join(relativeBase, ent.name);
    const abs = safeJoin(REPO_ROOT, rel);

    if (ent.isDirectory()) {
      files.push(...walkDir(abs, rel));
    } else if (ent.isFile()) {
      files.push({ abs, rel });
    } else {
      // includes symlinks/specials
      try {
        if (isSymlink(abs)) fail(`${relativeBase}: symlink not allowed: ${rel}`);
        else fail(`${relativeBase}: unsupported file type: ${rel}`);
      } catch {
        fail(`${relativeBase}: unsupported/special file: ${rel}`);
      }
    }
  }

  return files;
}

function getAllSkillDirs() {
  const rootEntries = fs.readdirSync(SKILLS_ROOT, { withFileTypes: true });

  return rootEntries
    .filter((e) => e.isDirectory() && !IGNORE_DIRS_AT_ROOT.has(e.name) && !e.name.startsWith("."))
    .map((e) => e.name);
}

// --skills 只保留仓库里真实存在的目录：本次改动若是删除技能，不该算校验失败
function getRequestedSkillDirs(allSkillDirs) {
  if (skillsArg === null) return null;

  const all = new Set(allSkillDirs);
  return skillsArg
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean)
    .filter((s) => all.has(s));
}

function main() {
  const allSkillDirs = getAllSkillDirs();
  const requested = getRequestedSkillDirs(allSkillDirs);
  const skillDirs = requested ?? allSkillDirs;

  if (skillDirs.length === 0) {
    if (requested) {
      ok("No matching skill directories to validate.");
      writeReport(skillDirs);
      process.exit(0);
    }

    currentSkill = "(repo)";
    fail("No skill directories found at repo root.");
    writeReport(skillDirs);
    process.exit(1);
  }

  ok(`Found ${skillDirs.length} skill directories.`);

  for (const skillName of skillDirs) {
    currentSkill = skillName;
    const failCountBefore = failCount;
    const skillPath = path.join(SKILLS_ROOT, skillName);
    const skillMd = path.join(skillPath, "SKILL.md");

    if (!fs.existsSync(skillMd)) {
      fail(`${skillName}: missing SKILL.md`);
      continue;
    }

    try {
      const parsed = parseFrontmatter(fs.readFileSync(skillMd, "utf8"));
      if (!parsed) fail(`${skillName}: SKILL.md must start with YAML frontmatter (---)`);
      else validateSkillFrontmatter(skillName, parsed.frontmatter);
    } catch (e) {
      fail(`${skillName}: invalid frontmatter: ${e?.message ?? String(e)}`);
    }

    const files = walkDir(skillPath, skillName);

    if (files.length > MAX_FILES_PER_SKILL) {
      fail(`${skillName}: too many files (${files.length}). Limit ${MAX_FILES_PER_SKILL}`);
    }

    for (const { abs, rel } of files) {
      // block symlinks (again, in case)
      try {
        if (isSymlink(abs)) {
          fail(`${skillName}: symlink not allowed: ${rel}`);
          continue;
        }
      } catch {
        fail(`${skillName}: could not stat file: ${rel}`);
        continue;
      }

      const base = path.basename(rel);
      const ext = path.extname(rel).toLowerCase();
      const isBinaryAsset = BINARY_ASSET_EXTENSIONS.has(ext);

      // 命中拒绝名单的文件不再走白名单判断，避免同一个文件报两条
      const isDenied = DENY_FILENAMES.has(base) || (DENY_EXTENSIONS.has(ext) && !isBinaryAsset);
      if (DENY_FILENAMES.has(base)) {
        fail(`${skillName}: denylisted filename: ${rel}`);
      } else if (DENY_EXTENSIONS.has(ext) && !isBinaryAsset) {
        fail(`${skillName}: denylisted extension "${ext}": ${rel}`);
      }

      const isAllowedByName = ALLOW_FILENAMES.has(base);
      if (!isDenied && !isAllowedByName && !isBinaryAsset) {
        if (ext) {
          if (!ALLOW_EXTENSIONS.has(ext) && base !== "SKILL.md") {
            fail(`${skillName}: extension "${ext}" not allowed: ${rel}`);
          }
        } else {
          // no-extension files are risky; treat as fail to be strict
          fail(`${skillName}: file without extension not allowed: ${rel}`);
        }
      }

      const st = fs.statSync(abs);
      if (st.size > MAX_FILE_BYTES) fail(`${skillName}: file too large (${st.size} bytes): ${rel}`);

      // ---- 二进制素材：不采样文本，改为核对文件头 ----
      if (isBinaryAsset) {
        try {
          const buf = readFileSample(abs, st.size);
          if (!matchesBinaryAssetSignature(ext, buf)) {
            fail(`${skillName}: file header does not match "${ext}": ${rel}`);
          }
        } catch (e) {
          fail(
            `${skillName}: could not sample file for asset header checks: ${rel} (${
              e?.message ?? String(e)
            })`
          );
        }
        continue;
      }

      // ---- Binary masquerading detection (FAIL fast) ----
      // If it's an allowed "text-ish" file, ensure it actually looks like text.
      const isTextAllowed =
        base === "SKILL.md" ||
        isAllowedByName ||
        (ext && ALLOW_EXTENSIONS.has(ext));

      if (isTextAllowed) {
        try {
          const buf = readFileSample(abs, st.size);
          if (buf.length > 0) {
            const magic = detectMagic(buf);
            if (magic) {
              fail(`${skillName}: binary masquerading detected (${magic}) in text file: ${rel}`);
            }

            const { nulFound, printableRatio, replacementRatio } = analyzeTextlikeness(buf);

            if (nulFound) {
              fail(`${skillName}: NUL byte found (binary content) in: ${rel}`);
            }

            if (printableRatio < MIN_PRINTABLE_RATIO) {
              fail(
                `${skillName}: low printable ratio (${printableRatio.toFixed(
                  2
                )}) in text file: ${rel}`
              );
            }

            if (replacementRatio > UTF8_REPLACEMENT_WARN_RATIO) {
              warn(
                `${skillName}: suspicious encoding (UTF-8 replacement ratio ${(replacementRatio * 100).toFixed(
                  2
                )}%) in: ${rel}`
              );
            }
          }
        } catch (e) {
          fail(
            `${skillName}: could not sample file for binary masquerading checks: ${rel} (${
              e?.message ?? String(e)
            })`
          );
        }
      }
    }

    if (failCount === failCountBefore) ok(`${skillName}: structure validated`);
  }

  writeReport(skillDirs);

  if (failCount > 0) {
    console.error("\nStructure validation FAILED.");
    process.exit(1);
  }

  console.log("\nStructure validation PASSED.");
  process.exit(0);
}

main();
