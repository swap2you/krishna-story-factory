import { createHmac, timingSafeEqual } from "node:crypto";
import type { ReadonlyRequestCookies } from "next/dist/server/web/spec-extension/adapters/request-cookies";

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

const SESSION_TTL_SECONDS = 60 * 60 * 12;

export function studioToken(): string {
  const configured = (process.env.BHAVA_STUDIO_BOOTSTRAP_TOKEN || "").trim();
  if (configured) return configured;
  // Default only allowed outside production; production must set the env.
  if (process.env.NODE_ENV === "production") {
    throw new Error("BHAVA_STUDIO_BOOTSTRAP_TOKEN must be set in production");
  }
  return "bhava-local-studio";
}

export function signStudioSession(role: string, nonce: string, expEpochSec?: number): string {
  const exp = String(expEpochSec ?? Math.floor(Date.now() / 1000) + SESSION_TTL_SECONDS);
  const payload = `${role}.${nonce}.${exp}`;
  const sig = createHmac("sha256", studioToken()).update(payload).digest("hex");
  return `${payload}.${sig}`;
}

export function verifyStudioSessionCookie(value: string | undefined): { ok: boolean; role?: string } {
  if (!value) return { ok: false };
  const parts = value.split(".");
  // role.nonce.exp.sig
  if (parts.length !== 4) return { ok: false };
  const [role, nonce, exp, sig] = parts;
  if (!ROLES.has(role) || !nonce || !exp || !sig) return { ok: false };
  const expNum = Number.parseInt(exp, 10);
  if (!Number.isFinite(expNum) || expNum < Math.floor(Date.now() / 1000)) return { ok: false };
  const expected = createHmac("sha256", studioToken()).update(`${role}.${nonce}.${exp}`).digest("hex");
  try {
    const a = Buffer.from(sig, "hex");
    const b = Buffer.from(expected, "hex");
    if (a.length !== b.length || !timingSafeEqual(a, b)) return { ok: false };
  } catch {
    return { ok: false };
  }
  return { ok: true, role };
}

export function isStudioAuthed(jar: ReadonlyRequestCookies): boolean {
  const session = jar.get("bhava_studio_session")?.value;
  const verified = verifyStudioSessionCookie(session);
  if (!verified.ok) return false;
  const roleCookie = jar.get("bhava_studio_role")?.value || "";
  return roleCookie === verified.role;
}

/**
 * Phase 1 loopback gate: trust only Host/localhost style signals.
 * Do NOT honor client-controlled X-Forwarded-For / X-Real-IP (forgeable).
 * Presence of forwarded headers indicates a proxied/non-direct request — reject.
 * Operators must bind the studio web process to 127.0.0.1 (see KNOWN_LIMITATIONS).
 */
export function isLoopbackRequest(hdrs: Headers): boolean {
  if (hdrs.get("x-forwarded-for") || hdrs.get("x-forwarded-host") || hdrs.get("x-real-ip")) {
    return false;
  }
  const host = (hdrs.get("host") || "").split(":")[0].toLowerCase();
  return host === "localhost" || host === "127.0.0.1" || host === "::1";
}
