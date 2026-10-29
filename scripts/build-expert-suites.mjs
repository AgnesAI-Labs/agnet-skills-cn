#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import zlib from "node:zlib";

/**
 * 专家套件打包脚本。
 *
 * 入口是 suites/<suite-id>/suite.json：只写组合声明，技能正文仍留在仓库根目录，
 * 构建时按声明把技能目录收进包内 skills/ 下，不复制、不改写技能内容。
 *
 * 输出 dist/expert-suites/<id>-<version>.zip，并打印 sha256。
 *
 * 打包限制逐条对齐后端预检（crates/goose-server/src/routes/expert_suite.rs:
 * MAX_ARCHIVE / MAX_EXPANDED / MAX_FILE / MAX_FILES / 路径层级），
 * 任何一项不满足都直接报错并指出套件、技能目录与具体文件。
 */

const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SUITES_DIR = path.join(REPO_ROOT, "suites");
const SERVERS_PATH = path.join(REPO_ROOT, "mcp", "servers.json");
const DIST_DIR = path.join(REPO_ROOT, "dist", "expert-suites");

const MIB = 1024 * 1024;

const MAX_ARCHIVE_BYTES = 60 * MIB;
const MAX_EXPANDED_BYTES = 80 * MIB;
const MAX_FILE_BYTES = 10 * MIB;
const MAX_ENTRIES = 2000;
const MAX_PATH_DEPTH = 16;

const SUITE_ID_RE = /^[a-z0-9][a-z0-9.-]*$/;
// 版本号会进文件名，只要求是文件系统安全的一段字符，具体格式由套件作者决定
const VERSION_RE = /^[0-9A-Za-z][0-9A-Za-z.+-]*$/;

// 固定 1980-01-01 00:00:00（DOS 日期原点）与固定权限位：
// 同一份输入必须产出完全相同的字节，重跑 sha256 不变。
const FIXED_DOS_DATE = (0 << 9) | (1 << 5) | 1;
const FIXED_DOS_TIME = 0;
const FIXED_FILE_MODE = 0o100644;

const REQUIRED_STRING_FIELDS = ["id", "name", "name_zh", "description", "description_zh", "version", "category"];

const problems = [];

function record(suiteId, message) {
  problems.push(`[${suiteId}] ${message}`);
}

function compareNames(a, b) {
  return a < b ? -1 : a > b ? 1 : 0;
}

function humanSize(bytes) {
  if (bytes >= MIB) return `${(bytes / MIB).toFixed(2)} MiB`;
  if (bytes >= 1024) return `${(bytes / 1024).toFixed(1)} KiB`;
  return `${bytes} B`;
}

// ------------------------------ 声明 ------------------------------

function listSuiteDeclarations() {
  const entries = fs.readdirSync(SUITES_DIR, { withFileTypes: true });
  const declarations = [];

  for (const entry of entries.sort((a, b) => compareNames(a.name, b.name))) {
    if (!entry.isDirectory() || entry.name.startsWith(".")) continue;
    const file = path.join(SUITES_DIR, entry.name, "suite.json");
    if (!fs.existsSync(file)) {
      record(entry.name, `missing suite.json under suites/${entry.name}/`);
      continue;
    }
    declarations.push({ dirName: entry.name, file });
  }

  return declarations;
}

function readServers() {
  const raw = JSON.parse(fs.readFileSync(SERVERS_PATH, "utf8"));
  const byId = new Map();
  for (const entry of raw) {
    if (entry && typeof entry.id === "string") byId.set(entry.id, entry);
  }
  return byId;
}

function validateStringList(suiteId, field, value) {
  if (!Array.isArray(value) || value.some((v) => typeof v !== "string" || !v.trim())) {
    record(suiteId, `"${field}" must be a list of non-empty strings`);
    return null;
  }
  const seen = new Set();
  for (const item of value) {
    if (seen.has(item)) record(suiteId, `"${field}" lists "${item}" twice`);
    seen.add(item);
  }
  return value;
}

// ------------------------------ 连接器 ------------------------------

function checkRemoteUrl(url) {
  let parsed;
  try {
    parsed = new URL(url);
  } catch {
    return "is not a valid URL";
  }
  if (parsed.protocol !== "http:" && parsed.protocol !== "https:") return "must use http or https";
  if (!parsed.hostname) return "must include a host";
  // 后端预检直接拒绝带 query、fragment 或凭据的 URL，这里提前拦下
  if (parsed.search) return "must not contain a query string";
  if (parsed.hash) return "must not contain a fragment";
  if (parsed.username || parsed.password) return "must not contain credentials";
  return null;
}

function connectorFromServer(suiteId, id, entry) {
  const hasUrl = typeof entry.url === "string" && entry.url.trim() !== "";
  const hasCommand = typeof entry.command === "string" && entry.command.trim() !== "";

  if (hasUrl && hasCommand) {
    record(suiteId, `connector "${id}" has both url and command in mcp/servers.json; cannot tell which transport to use`);
    return null;
  }

  if (hasUrl) {
    const url = entry.url.trim();
    const invalid = checkRemoteUrl(url);
    if (invalid) {
      record(suiteId, `connector "${id}" url ${invalid}: ${url}`);
      return null;
    }
    return { type: "streamable-http", url };
  }

  if (hasCommand) {
    const [command, ...args] = entry.command.trim().split(/\s+/);
    return { command, args };
  }

  record(suiteId, `connector "${id}" has neither url nor command in mcp/servers.json`);
  return null;
}

function resolveConnectors(suiteId, ids, servers) {
  const mcpServers = {};

  for (const id of ids) {
    const entry = servers.get(id);
    if (!entry) {
      record(suiteId, `connector "${id}" is not an id in mcp/servers.json`);
      continue;
    }
    const config = connectorFromServer(suiteId, id, entry);
    if (config) mcpServers[id] = config;
  }

  return mcpServers;
}

// ------------------------------ 技能 ------------------------------

function resolveSkill(suiteId, name) {
  if (/[/\\]/.test(name) || name === "." || name === "..") {
    record(suiteId, `skill "${name}" must be a directory name at the repo root, not a path`);
    return null;
  }

  const dir = path.join(REPO_ROOT, name);
  if (!fs.existsSync(dir)) {
    record(suiteId, `skill "${name}": directory not found at repo root`);
    return null;
  }

  const stat = fs.lstatSync(dir);
  if (stat.isSymbolicLink()) {
    record(suiteId, `skill "${name}": directory must not be a symlink`);
    return null;
  }
  if (!stat.isDirectory()) {
    record(suiteId, `skill "${name}": not a directory`);
    return null;
  }
  if (!fs.existsSync(path.join(dir, "SKILL.md"))) {
    record(suiteId, `skill "${name}": missing SKILL.md`);
    return null;
  }

  return { name, dir };
}

function collectSkillFiles(suiteId, skill) {
  const prefix = `skills/${skill.name}`;
  const entries = [];

  const walk = (absDir, relDir) => {
    const children = fs.readdirSync(absDir, { withFileTypes: true }).sort((a, b) =>
      compareNames(a.name, b.name)
    );

    for (const child of children) {
      const abs = path.join(absDir, child.name);
      const rel = relDir ? `${relDir}/${child.name}` : child.name;

      if (child.isSymbolicLink()) {
        record(suiteId, `skill "${skill.name}": symlink not allowed: ${prefix}/${rel}`);
        continue;
      }
      if (child.isDirectory()) {
        walk(abs, rel);
        continue;
      }
      if (!child.isFile()) {
        record(suiteId, `skill "${skill.name}": unsupported file type: ${prefix}/${rel}`);
        continue;
      }

      const st = fs.statSync(abs);
      entries.push({ name: `${prefix}/${rel}`, absPath: abs, size: st.size, skill: skill.name });
    }
  };

  walk(skill.dir, "");
  return entries;
}

// ------------------------------ plugin.json ------------------------------

function buildPluginManifest(suite, mcpServers) {
  const manifest = {
    name: suite.id,
    version: suite.version,
    displayName: suite.name,
    displayNameZh: suite.name_zh,
    description: suite.description,
    descriptionZh: suite.description_zh,
    category: suite.category,
    tags: suite.tags,
  };

  if (Object.keys(mcpServers).length > 0) manifest.mcpServers = mcpServers;

  return Buffer.from(`${JSON.stringify(manifest, null, 2)}\n`, "utf8");
}

// ------------------------------ ZIP ------------------------------

const CRC_TABLE = (() => {
  const table = new Uint32Array(256);
  for (let i = 0; i < 256; i++) {
    let c = i;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    table[i] = c >>> 0;
  }
  return table;
})();

function crc32(buf) {
  let c = 0xffffffff;
  for (let i = 0; i < buf.length; i++) c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

// 手写 ZIP：仓库没有依赖清单，不想为打包引入 npm 包。
// 只实现 store 与 deflate 两种方式，条目数、大小都远低于 zip64 门槛。
function buildZip(files) {
  const localChunks = [];
  const centralChunks = [];
  let offset = 0;

  for (const file of files) {
    const nameBuf = Buffer.from(file.name, "utf8");
    const deflated = zlib.deflateRawSync(file.data, { level: 9 });
    const useDeflate = deflated.length < file.data.length;
    const payload = useDeflate ? deflated : file.data;
    const method = useDeflate ? 8 : 0;
    const checksum = crc32(file.data);

    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034b50, 0);
    local.writeUInt16LE(20, 4);
    local.writeUInt16LE(0x0800, 6); // 文件名按 UTF-8
    local.writeUInt16LE(method, 8);
    local.writeUInt16LE(FIXED_DOS_TIME, 10);
    local.writeUInt16LE(FIXED_DOS_DATE, 12);
    local.writeUInt32LE(checksum, 14);
    local.writeUInt32LE(payload.length, 18);
    local.writeUInt32LE(file.data.length, 22);
    local.writeUInt16LE(nameBuf.length, 26);
    local.writeUInt16LE(0, 28);

    const central = Buffer.alloc(46);
    central.writeUInt32LE(0x02014b50, 0);
    central.writeUInt16LE(0x031e, 4); // made by unix, 3.0
    central.writeUInt16LE(20, 6);
    central.writeUInt16LE(0x0800, 8);
    central.writeUInt16LE(method, 10);
    central.writeUInt16LE(FIXED_DOS_TIME, 12);
    central.writeUInt16LE(FIXED_DOS_DATE, 14);
    central.writeUInt32LE(checksum, 16);
    central.writeUInt32LE(payload.length, 20);
    central.writeUInt32LE(file.data.length, 24);
    central.writeUInt16LE(nameBuf.length, 28);
    central.writeUInt16LE(0, 30);
    central.writeUInt16LE(0, 32);
    central.writeUInt16LE(0, 34);
    central.writeUInt16LE(0, 36);
    central.writeUInt32LE((FIXED_FILE_MODE << 16) >>> 0, 38);
    central.writeUInt32LE(offset, 42);

    localChunks.push(local, nameBuf, payload);
    centralChunks.push(central, nameBuf);
    offset += local.length + nameBuf.length + payload.length;
  }

  const centralBuf = Buffer.concat(centralChunks);
  const eocd = Buffer.alloc(22);
  eocd.writeUInt32LE(0x06054b50, 0);
  eocd.writeUInt16LE(0, 4);
  eocd.writeUInt16LE(0, 6);
  eocd.writeUInt16LE(files.length, 8);
  eocd.writeUInt16LE(files.length, 10);
  eocd.writeUInt32LE(centralBuf.length, 12);
  eocd.writeUInt32LE(offset, 16);
  eocd.writeUInt16LE(0, 20);

  return Buffer.concat([...localChunks, centralBuf, eocd]);
}

// ------------------------------ 构建 ------------------------------

function readSuiteDeclaration(declaration) {
  const fileName = path.relative(REPO_ROOT, declaration.file);

  let raw;
  try {
    raw = JSON.parse(fs.readFileSync(declaration.file, "utf8"));
  } catch (e) {
    record(declaration.dirName, `${fileName} is not valid JSON (${e?.message ?? String(e)})`);
    return null;
  }

  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    record(declaration.dirName, `${fileName} must be a JSON object`);
    return null;
  }

  const suiteId = typeof raw.id === "string" && raw.id.trim() ? raw.id.trim() : declaration.dirName;
  let ok = true;

  for (const field of REQUIRED_STRING_FIELDS) {
    const value = raw[field];
    if (typeof value !== "string" || !value.trim()) {
      record(suiteId, `"${field}" must be a non-empty string`);
      ok = false;
    }
  }

  if (typeof raw.id === "string" && raw.id.trim()) {
    if (raw.id.length > 64 || !SUITE_ID_RE.test(raw.id)) {
      record(suiteId, '"id" must match ^[a-z0-9][a-z0-9.-]*$ and be at most 64 characters');
      ok = false;
    }
  }

  if (typeof raw.version === "string" && raw.version.trim() && !VERSION_RE.test(raw.version)) {
    record(suiteId, `"version" must be a filename-safe string, got "${raw.version}"`);
    ok = false;
  }

  const tags = validateStringList(suiteId, "tags", raw.tags);
  if (!tags || tags.length === 0) {
    record(suiteId, '"tags" must not be empty');
    ok = false;
  }

  const skills = validateStringList(suiteId, "skills", raw.skills);
  if (!skills || skills.length === 0) {
    record(suiteId, '"skills" must list at least one skill directory');
    ok = false;
  }

  const connectors = raw.connectors === undefined ? [] : validateStringList(suiteId, "connectors", raw.connectors);
  if (connectors === null) ok = false;

  if (!ok) return null;

  return {
    id: raw.id.trim(),
    version: raw.version.trim(),
    name: raw.name.trim(),
    name_zh: raw.name_zh.trim(),
    description: raw.description.trim(),
    description_zh: raw.description_zh.trim(),
    category: raw.category.trim(),
    tags,
    skills,
    connectors,
  };
}

function buildSuite(suite, servers) {
  // 技能与连接器各自完整解析一遍，问题一次报全，不因前一项失败就吞掉后一项
  const skills = [];
  for (const name of suite.skills) {
    const skill = resolveSkill(suite.id, name);
    if (skill) skills.push(skill);
  }

  const mcpServers = resolveConnectors(suite.id, suite.connectors, servers);

  if (skills.length !== suite.skills.length || Object.keys(mcpServers).length !== suite.connectors.length) {
    return null;
  }

  const skillFiles = skills.flatMap((skill) => collectSkillFiles(suite.id, skill));
  const pluginJson = buildPluginManifest(suite, mcpServers);

  const manifestCheck = JSON.parse(pluginJson.toString("utf8"));
  if (manifestCheck.name !== suite.id) {
    record(suite.id, `generated plugin.json name "${manifestCheck.name}" does not match suite id`);
    return null;
  }

  const files = [{ name: "plugin.json", data: pluginJson, size: pluginJson.length }, ...skillFiles.map((f) => ({
    name: f.name,
    data: fs.readFileSync(f.absPath),
    size: f.size,
  }))];

  files.sort((a, b) => compareNames(a.name, b.name));

  return { suite, files };
}

function selfCheck(pkg) {
  const { suite, files } = pkg;
  let ok = true;

  if (files.length > MAX_ENTRIES) {
    record(suite.id, `package has ${files.length} entries, limit is ${MAX_ENTRIES}`);
    ok = false;
  }

  const seen = new Set();
  for (const file of files) {
    if (seen.has(file.name)) {
      record(suite.id, `duplicate entry path: ${file.name}`);
      ok = false;
    }
    seen.add(file.name);

    if (file.name.split("/").length > MAX_PATH_DEPTH) {
      record(suite.id, `path deeper than ${MAX_PATH_DEPTH} segments: ${file.name}`);
      ok = false;
    }
    if (file.size > MAX_FILE_BYTES) {
      record(suite.id, `file larger than ${humanSize(MAX_FILE_BYTES)}: ${file.name} (${humanSize(file.size)})`);
      ok = false;
    }
  }

  const expanded = files.reduce((sum, file) => sum + file.size, 0);
  if (expanded > MAX_EXPANDED_BYTES) {
    record(suite.id, `expanded size ${humanSize(expanded)} exceeds ${humanSize(MAX_EXPANDED_BYTES)}`);
    ok = false;
  }

  if (!files.some((file) => file.name === "plugin.json")) {
    record(suite.id, "package root has no plugin.json");
    ok = false;
  }
  if (!files.some((file) => file.name.endsWith("/SKILL.md"))) {
    record(suite.id, "package contains no SKILL.md");
    ok = false;
  }

  return ok;
}

function packSuite(pkg) {
  const { suite, files } = pkg;
  const expanded = files.reduce((sum, file) => sum + file.size, 0);
  const largest = files.reduce((max, file) => (file.size > max.size ? file : max), files[0]);

  const archive = buildZip(files);
  if (archive.length > MAX_ARCHIVE_BYTES) {
    record(
      suite.id,
      `archive ${humanSize(archive.length)} exceeds ${humanSize(MAX_ARCHIVE_BYTES)} (expanded ${humanSize(expanded)})`
    );
    return null;
  }

  return {
    suite,
    archive,
    entries: files.length,
    expanded,
    largest,
    archiveBytes: archive.length,
    sha256: crypto.createHash("sha256").update(archive).digest("hex"),
  };
}

function writePackage(result) {
  fs.mkdirSync(DIST_DIR, { recursive: true });
  const target = path.join(DIST_DIR, `${result.suite.id}-${result.suite.version}.zip`);
  fs.writeFileSync(target, result.archive);
  return target;
}

function main() {
  if (!fs.existsSync(SUITES_DIR)) {
    console.error(`❌ suites/ not found at ${SUITES_DIR}`);
    process.exit(1);
  }

  const declarations = listSuiteDeclarations();
  if (declarations.length === 0) {
    console.error("❌ No suite declarations found under suites/");
    process.exit(1);
  }

  const servers = readServers();
  const packed = [];

  // 先全部校验与打包，确认没有问题再落盘：任一失败时不留下半成品
  for (const declaration of declarations) {
    const suite = readSuiteDeclaration(declaration);
    if (!suite) continue;

    const pkg = buildSuite(suite, servers);
    if (!pkg) continue;
    if (!selfCheck(pkg)) continue;

    const result = packSuite(pkg);
    if (result) packed.push(result);
  }

  if (problems.length > 0) {
    console.error("\nExpert suite build FAILED:");
    for (const problem of problems) console.error(`  ❌ ${problem}`);
    process.exit(1);
  }

  const built = packed.map((result) => ({ ...result, target: writePackage(result) }));

  for (const result of built) {
    console.log(`\n✅ ${result.suite.id} ${result.suite.version}`);
    console.log(`   package:  ${path.relative(REPO_ROOT, result.target)}`);
    console.log(`   entries:  ${result.entries} (skills ${result.suite.skills.length}, connectors ${result.suite.connectors.length})`);
    console.log(`   max file: ${humanSize(result.largest.size)}  ${result.largest.name}`);
    console.log(`   expanded: ${humanSize(result.expanded)} / ${humanSize(MAX_EXPANDED_BYTES)}`);
    console.log(`   archive:  ${humanSize(result.archiveBytes)} / ${humanSize(MAX_ARCHIVE_BYTES)}`);
    console.log("   symlinks: none");
    console.log(`   sha256:   ${result.sha256}`);
  }

  console.log(`\nBuilt ${built.length} expert suite package(s).`);
  process.exit(0);
}

main();
