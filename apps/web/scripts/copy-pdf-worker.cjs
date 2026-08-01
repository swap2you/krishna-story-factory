/**
 * Copy pdf.js worker into public/ so Next standalone + CI serve it without CDN.
 */
const fs = require("node:fs");
const path = require("node:path");

const candidates = [
  path.resolve(__dirname, "../../../node_modules/pdfjs-dist/build/pdf.worker.min.mjs"),
  path.resolve(__dirname, "../node_modules/pdfjs-dist/build/pdf.worker.min.mjs"),
];
const src = candidates.find((p) => fs.existsSync(p));
const destDir = path.resolve(__dirname, "../public/pdfjs");
const dest = path.join(destDir, "pdf.worker.min.mjs");

if (!src) {
  console.warn("[copy-pdf-worker] pdf.worker.min.mjs not found; skip");
  process.exit(0);
}

fs.mkdirSync(destDir, { recursive: true });
fs.copyFileSync(src, dest);
console.log(`[copy-pdf-worker] ${src} -> ${dest}`);
