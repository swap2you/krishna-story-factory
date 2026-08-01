import { NextRequest, NextResponse } from "next/server";

const PRIVATE_PREFIXES = [
  "/studio",
  "/dev",
  "/api/studio",
  "/api/v1/factory",
  "/api/v1/scheduler",
  "/api/v1/queue",
  "/api/v1/local",
];

const CSP = [
  "default-src 'self'",
  "base-uri 'self'",
  "object-src 'none'",
  "frame-ancestors 'none'",
  "form-action 'self' mailto:",
  "img-src 'self' data: blob:",
  "media-src 'self' blob:",
  "font-src 'self' data:",
  "style-src 'self' 'unsafe-inline'",
  "script-src 'self' 'unsafe-inline'",
  "connect-src 'self'",
  "worker-src 'self' blob:",
  "manifest-src 'self'",
  "upgrade-insecure-requests",
].join("; ");

function isPrivate(pathname: string): boolean {
  return PRIVATE_PREFIXES.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`),
  );
}

function isPublicSite(): boolean {
  const flag = (process.env.BHAVA_PUBLIC_SITE || "").trim().toLowerCase();
  if (flag === "0" || flag === "false" || flag === "off") return false;
  if (flag === "1" || flag === "true" || flag === "on") return true;
  // Default public for production containers; operators can force local mode with BHAVA_PUBLIC_SITE=0.
  return process.env.NODE_ENV === "production";
}

function applyHeaders(response: NextResponse): NextResponse {
  const publicSite = isPublicSite();
  if (publicSite) response.headers.set("Content-Security-Policy", CSP);
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("Cross-Origin-Opener-Policy", "same-origin");
  response.headers.set("Cross-Origin-Resource-Policy", "same-origin");
  response.headers.set(
    "Permissions-Policy",
    "accelerometer=(), autoplay=(self), camera=(), geolocation=(), gyroscope=(), microphone=(), payment=(), usb=()",
  );
  return response;
}

export function middleware(request: NextRequest) {
  const publicSite = isPublicSite();

  if (publicSite && isPrivate(request.nextUrl.pathname)) {
    return applyHeaders(new NextResponse(null, { status: 404 }));
  }

  if (
    publicSite &&
    request.nextUrl.pathname.startsWith("/api/") &&
    !["GET", "HEAD", "OPTIONS"].includes(request.method)
  ) {
    return applyHeaders(new NextResponse(null, { status: 405 }));
  }

  return applyHeaders(NextResponse.next());
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
