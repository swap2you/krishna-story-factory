/**
 * npm optionalDependencies + workspaces can skip platform natives (npm/cli#4828).
 * Install the current platform package when missing; never fail other OSes.
 */
const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const root = path.resolve(__dirname, "..");

function ensurePackage(pkg, version) {
  const target = path.join(root, "node_modules", ...pkg.split("/"));
  if (fs.existsSync(path.join(target, "package.json"))) return;
  console.log(`[bhava] extracting optional native package ${pkg}@${version}`);
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "bhava-native-"));
  try {
    const pack = spawnSync("npm", ["pack", `${pkg}@${version}`], {
      cwd: tmp,
      encoding: "utf8",
      shell: true,
    });
    if (pack.status !== 0) {
      console.warn(`[bhava] npm pack failed for ${pkg}`);
      return;
    }
    const tgz = (pack.stdout || "").trim().split(/\r?\n/).filter(Boolean).pop();
    if (!tgz) {
      console.warn(`[bhava] no tarball for ${pkg}`);
      return;
    }
    const extract = spawnSync("tar", ["-xf", tgz], { cwd: tmp, shell: true, encoding: "utf8" });
    if (extract.status !== 0) {
      console.warn(`[bhava] tar extract failed for ${pkg}: ${extract.stderr || ""}`);
      return;
    }
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.rmSync(target, { recursive: true, force: true });
    fs.renameSync(path.join(tmp, "package"), target);
    console.log(`[bhava] installed ${pkg} -> ${target}`);
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
}

if (process.platform === "win32" && process.arch === "x64") {
  ensurePackage("@rollup/rollup-win32-x64-msvc", "4.62.2");
  ensurePackage("@next/swc-win32-x64-msvc", "15.3.5");
} else if (process.platform === "linux" && process.arch === "x64") {
  ensurePackage("@rollup/rollup-linux-x64-gnu", "4.62.2");
} else if (process.platform === "darwin" && process.arch === "arm64") {
  ensurePackage("@rollup/rollup-darwin-arm64", "4.62.2");
} else if (process.platform === "darwin" && process.arch === "x64") {
  ensurePackage("@rollup/rollup-darwin-x64", "4.62.2");
}
