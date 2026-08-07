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
 * Phase 1 loopback gate.
 * - Host must be localhost / 127.0.0.1 / ::1
 * - Do not treat arbitrary X-Forwarded-* as proof of loopback
 * - If forwarded headers are present, every hop must itself be loopback
 *   (Next may attach X-Forwarded-For=127.0.0.1 on local requests)
 * Operators should still bind the studio web process to 127.0.0.1.
 */
export function isLoopbackRequest(hdrs: Headers): boolean {
  const host = (hdrs.get("host") || "").split(":")[0].toLowerCase();
  if (!(host === "localhost" || host === "127.0.0.1" || host === "::1")) {
    return false;
  }
  const forwardedHost = (hdrs.get("x-forwarded-host") || "").split(",")[0].trim().split(":")[0].toLowerCase();
  if (forwardedHost && !(forwardedHost === "localhost" || forwardedHost === "127.0.0.1" || forwardedHost === "::1")) {
    return false;
  }
  const xff = (hdrs.get("x-forwarded-for") || "").trim();
  if (xff) {
    const hops = xff.split(",").map((h) => h.trim().toLowerCase());
    const loopbackHop = (h: string) =>
      h === "127.0.0.1" || h === "::1" || h === "localhost" || h === "::ffff:127.0.0.1";
    if (!hops.every(loopbackHop)) return false;
  }
  const realIp = (hdrs.get("x-real-ip") || "").trim().toLowerCase();
  if (realIp && !(realIp === "127.0.0.1" || realIp === "::1" || realIp === "::ffff:127.0.0.1")) {
    return false;
  }
  return true;
}
