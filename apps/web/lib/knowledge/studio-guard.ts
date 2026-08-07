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

/** Parse Host / X-Forwarded-Host into a bare hostname (no port). */
export function parseHostName(hostHeader: string | null | undefined): string {
  const raw = (hostHeader || "").trim().toLowerCase();
  if (!raw) return "";
  if (raw.startsWith("[")) {
    const end = raw.indexOf("]");
    if (end > 0) return raw.slice(1, end);
    return raw.replace(/^\[|\]$/g, "");
  }
  const colonCount = (raw.match(/:/g) || []).length;
  // IPv6 without brackets (rare in Host) — keep whole string.
  if (colonCount > 1) return raw;
  return raw.split(":")[0] || "";
}

export function isLoopbackHostName(host: string): boolean {
  const h = (host || "").trim().toLowerCase().replace(/^\[|\]$/g, "");
  if (!h) return false;
  if (h === "localhost" || h === "::1") return true;
  if (/^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(h)) return true;
  // IPv4-mapped IPv6
  if (h.startsWith("::ffff:")) {
    const mapped = h.slice("::ffff:".length);
    if (/^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(mapped)) return true;
    if (mapped === "127.0.0.1") return true;
  }
  return false;
}

/**
 * Phase 1 loopback gate.
 * Host must be loopback. Forwarded headers, when present, must also be loopback-only.
 * Operators should still bind the studio web process to 127.0.0.1.
 */
export function isLoopbackRequest(hdrs: Headers): boolean {
  const host = parseHostName(hdrs.get("host"));
  if (!isLoopbackHostName(host)) return false;

  const forwardedHost = parseHostName((hdrs.get("x-forwarded-host") || "").split(",")[0]);
  if (forwardedHost && !isLoopbackHostName(forwardedHost)) return false;

  const xff = (hdrs.get("x-forwarded-for") || "").trim();
  if (xff) {
    const hops = xff.split(",").map((part) => part.trim().toLowerCase());
    if (!hops.every((hop) => isLoopbackHostName(hop))) return false;
  }

  const realIp = (hdrs.get("x-real-ip") || "").trim().toLowerCase();
  if (realIp && !isLoopbackHostName(realIp)) return false;

  return true;
}
