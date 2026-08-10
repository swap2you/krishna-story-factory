import { NextRequest, NextResponse } from "next/server";
import { headers } from "next/headers";
import { randomUUID } from "node:crypto";
import { isLoopbackRequest, signStudioSession, studioToken } from "@/lib/knowledge/studio-guard";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const ROLES = new Set([
  "steward",
  "administrator",
  "contributor",
  "content_editor",
  "scriptural_reviewer",
  "devotional_reviewer",
  "copy_editor",
  "moderator",
  "auditor",
]);

export async function POST(req: NextRequest) {
  const hdrs = await headers();
  if (!isLoopbackRequest(hdrs)) {
    return NextResponse.json({ detail: "Studio bootstrap requires loopback host" }, { status: 403 });
  }
  const body = (await req.json().catch(() => ({}))) as {
    role?: string;
    bootstrap_token?: string;
  };
  const role = (body.role || "").trim();
  const token = (body.bootstrap_token || "").trim();
  if (!ROLES.has(role)) {
    return NextResponse.json({ detail: "Unknown role" }, { status: 400 });
  }
  if (token !== studioToken()) {
    return NextResponse.json({ detail: "Invalid bootstrap token" }, { status: 403 });
  }
  const nonce = randomUUID();
  const session = signStudioSession(role, nonce);
  const secure = process.env.NODE_ENV === "production";
  const res = NextResponse.json({ ok: true, role });
  res.cookies.set("bhava_studio_session", session, {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    secure,
    maxAge: 60 * 60 * 12,
  });
  res.cookies.set("bhava_studio_role", role, {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    secure,
    maxAge: 60 * 60 * 12,
  });
  return res;
}

export async function DELETE() {
  const res = NextResponse.json({ ok: true });
  res.cookies.set("bhava_studio_session", "", { httpOnly: true, path: "/", maxAge: 0 });
  res.cookies.set("bhava_studio_role", "", { httpOnly: true, path: "/", maxAge: 0 });
  return res;
}
