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
  if (!/^\d{3}$/.test(padded)) {
    return NextResponse.json({ detail: "Story not found" }, { status: 404 });
  }
  if (!ALLOWED.has(filename) || filename.includes("..") || filename.includes("/") || filename.includes("\\")) {
    return NextResponse.json({ detail: "Asset not found" }, { status: 404 });
  }
  const upstream = `${apiOrigin()}/api/v1/stories/${padded}/assets/${filename}`;
  const headers = new Headers();
  const range = req.headers.get("range");
  if (range) headers.set("range", range);
  const accept = req.headers.get("accept");
  if (accept) headers.set("accept", accept);

  const controller = new AbortController();
  const onAbort = () => controller.abort();
  req.signal.addEventListener("abort", onAbort);

  try {
    const response = await fetch(upstream, {
      method,
      headers,
      cache: "no-store",
      signal: controller.signal,
      redirect: "manual",
    });

    if (response.status >= 300 && response.status < 400) {
      return NextResponse.json({ detail: "Upstream redirect not allowed" }, { status: 502 });
    }

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
    // Prevent intermediary transforms that break HTMLMediaElement.
    out.set("x-content-type-options", "nosniff");

    if (method === "HEAD") {
      return new NextResponse(null, { status: response.status, headers: out });
    }

    // Buffer body so media elements receive a complete, seekable payload with Content-Length.
    const buffer = await response.arrayBuffer();
    if (!out.has("content-length")) out.set("content-length", String(buffer.byteLength));
    return new NextResponse(buffer, { status: response.status, headers: out });
  } finally {
    req.signal.removeEventListener("abort", onAbort);
  }
}

export async function GET(req: NextRequest, ctx: Ctx) {
  return proxy(req, ctx, "GET");
}

export async function HEAD(req: NextRequest, ctx: Ctx) {
  return proxy(req, ctx, "HEAD");
}
