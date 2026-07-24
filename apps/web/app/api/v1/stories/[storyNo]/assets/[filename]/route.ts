import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function apiOrigin(): string {
  if (process.env.BHAVA_API_ORIGIN?.trim()) {
    return process.env.BHAVA_API_ORIGIN.trim().replace(/\/$/, "");
  }
  const url = process.env.BHAVA_API_URL?.trim();
  if (url) return url.replace(/\/api\/v1\/?$/, "").replace(/\/$/, "");
  return "http://127.0.0.1:8000";
}

const ALLOWED = new Set([
  "story.md",
  "narration.mp3",
  "story_poster.png",
  "coloring_page.png",
  "simple_coloring_page.png",
  "activity_sheet.pdf",
  "whatsapp_caption.txt",
  "manifest.json",
]);

type Ctx = { params: Promise<{ storyNo: string; filename: string }> };

async function proxy(req: NextRequest, ctx: Ctx, method: "GET" | "HEAD") {
  const { storyNo, filename } = await ctx.params;
  const padded = storyNo.padStart(3, "0");
  if (!ALLOWED.has(filename)) {
    return NextResponse.json({ detail: "Asset not found" }, { status: 404 });
  }
  const upstream = `${apiOrigin()}/api/v1/stories/${padded}/assets/${filename}`;
  const headers = new Headers();
  const range = req.headers.get("range");
  if (range) headers.set("range", range);
  const accept = req.headers.get("accept");
  if (accept) headers.set("accept", accept);

  const response = await fetch(upstream, {
    method,
    headers,
    cache: "no-store",
  });

  const out = new Headers();
  for (const key of [
    "content-type",
    "content-length",
    "content-range",
    "accept-ranges",
    "etag",
    "last-modified",
    "cache-control",
  ]) {
    const value = response.headers.get(key);
    if (value) out.set(key, value);
  }
  if (!out.has("accept-ranges")) out.set("accept-ranges", "bytes");
  out.set("cache-control", "public, max-age=60");

  if (method === "HEAD") {
    return new NextResponse(null, { status: response.status, headers: out });
  }
  return new NextResponse(response.body, { status: response.status, headers: out });
}

export async function GET(req: NextRequest, ctx: Ctx) {
  return proxy(req, ctx, "GET");
}

export async function HEAD(req: NextRequest, ctx: Ctx) {
  return proxy(req, ctx, "HEAD");
}
