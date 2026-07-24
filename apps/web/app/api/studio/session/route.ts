import { NextRequest, NextResponse } from "next/server";

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

function expectedToken(): string {
  return (process.env.BHAVA_STUDIO_BOOTSTRAP_TOKEN || "bhava-local-studio").trim();
}

export async function POST(req: NextRequest) {
  const body = (await req.json().catch(() => ({}))) as {
    role?: string;
    bootstrap_token?: string;
  };
  const role = (body.role || "").trim();
  const token = (body.bootstrap_token || "").trim();
  if (!ROLES.has(role)) {
    return NextResponse.json({ detail: "Unknown role" }, { status: 400 });
  }
  if (token !== expectedToken()) {
    return NextResponse.json({ detail: "Invalid bootstrap token" }, { status: 403 });
  }
  const res = NextResponse.json({ ok: true, role });
  res.cookies.set("bhava_studio_session", crypto.randomUUID(), {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    secure: false,
    maxAge: 60 * 60 * 12,
  });
  res.cookies.set("bhava_studio_role", role, {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    secure: false,
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
