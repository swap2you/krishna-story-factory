import { cookies, headers } from "next/headers";
import { NextRequest, NextResponse } from "next/server";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { isLoopbackRequest, isStudioAuthed } from "@/lib/knowledge/studio-guard";
import { getKnowledgePackage } from "@/lib/knowledge/packages";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function repoRoot(): string {
  const candidates = [
    path.join(process.cwd(), "..", ".."),
    process.cwd(),
    path.resolve(process.cwd(), "../.."),
  ];
  for (const c of candidates) {
    if (fs.existsSync(path.join(c, "content", "knowledge", "packages"))) return c;
  }
  return path.resolve(process.cwd(), "../..");
}

function pythonBin(root: string): string {
  const win = path.join(root, ".venv", "Scripts", "python.exe");
  const nix = path.join(root, ".venv", "bin", "python");
  if (fs.existsSync(win)) return win;
  if (fs.existsSync(nix)) return nix;
  return "python";
}

function safeFilename(slug: string, format: string): string {
  const cleaned = slug.replace(/[^a-z0-9-]/gi, "").toLowerCase() || "export";
  return `${cleaned}.${format}`;
}

export async function GET(
  req: NextRequest,
  ctx: { params: Promise<{ slug: string }> },
) {
  const { slug } = await ctx.params;
  const jar = await cookies();
  const hdrs = await headers();
  if (!isStudioAuthed(jar) || !isLoopbackRequest(hdrs)) {
    return new NextResponse(null, { status: 404 });
  }

  const format = (req.nextUrl.searchParams.get("format") || "pdf").toLowerCase();
  if (format !== "pdf" && format !== "docx") {
    return NextResponse.json({ detail: "format must be pdf or docx" }, { status: 400 });
  }

  const pkg = getKnowledgePackage(slug);
  if (!pkg) return new NextResponse(null, { status: 404 });
  if (pkg.record.visibility === "public") {
    return new NextResponse(null, { status: 404 });
  }

  const root = repoRoot();
  const outDir = fs.mkdtempSync(path.join(os.tmpdir(), "bhava-export-"));
  const outFile = path.join(outDir, `export.${format}`);
  const manifestFile = path.join(outDir, "manifest.json");
  try {
    const py = `
import json, sys
sys.path.insert(0, r${JSON.stringify(path.join(root, "apps", "api"))})
from bhava_api.knowledge.packages import get_package, render_pdf, render_docx
slug = ${JSON.stringify(slug)}
fmt = ${JSON.stringify(format)}
pkg = get_package(slug)
assert pkg is not None
if fmt == "pdf":
    data, manifest = render_pdf(pkg)
else:
    data, manifest = render_docx(pkg)
open(r${JSON.stringify(outFile)}, "wb").write(data)
open(r${JSON.stringify(manifestFile)}, "w", encoding="utf-8").write(json.dumps(manifest, indent=2))
print(manifest["canonical_content_hash"])
`;
    const result = spawnSync(pythonBin(root), ["-c", py], {
      encoding: "utf-8",
      cwd: root,
    });
    if (result.status !== 0) {
      return NextResponse.json({ detail: "export failed" }, { status: 500 });
    }
    const bytes = fs.readFileSync(outFile);
    const contentType =
      format === "pdf"
        ? "application/pdf"
        : "application/vnd.openxmlformats-officedocument.wordprocessingml.document";
    return new NextResponse(bytes, {
      status: 200,
      headers: {
        "Content-Type": contentType,
        "Content-Disposition": `attachment; filename="${safeFilename(pkg.record.slug, format)}"`,
        "X-Bhava-Canonical-Hash": result.stdout.trim().split(/\r?\n/).pop() || "",
        "Cache-Control": "no-store",
        "X-Robots-Tag": "noindex, nofollow, noarchive",
      },
    });
  } finally {
    try {
      fs.rmSync(outDir, { recursive: true, force: true });
    } catch {
      /* ignore cleanup errors */
    }
  }
}
