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

type Ctx = { params: Promise<{ storyNo: string }> };

export async function GET(_req: NextRequest, ctx: Ctx) {
  const { storyNo } = await ctx.params;
  const padded = storyNo.padStart(3, "0");
  const upstream = `${apiOrigin()}/api/v1/stories/${padded}/waveform`;
  const response = await fetch(upstream, { cache: "no-store" });
  const body = await response.arrayBuffer();
  return new NextResponse(body, {
    status: response.status,
    headers: {
      "content-type": response.headers.get("content-type") || "application/json",
      "cache-control": "public, max-age=120",
    },
  });
}
