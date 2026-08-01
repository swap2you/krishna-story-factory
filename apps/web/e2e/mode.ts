/**
 * Which application mode the browser suite is exercising.
 *
 * `public` mirrors production: private surfaces are blocked and only Stories
 * 001-009 exist. `local` is an operator workstation where Studio is reachable.
 * CI runs both, so neither set of expectations can rot unnoticed.
 */
export type AppMode = "public" | "local";

export const appMode: AppMode = process.env.BHAVA_E2E_MODE === "local" ? "local" : "public";
export const isPublicMode = appMode === "public";
export const isLocalMode = appMode === "local";

/** Route prefixes that must never be reachable on the public site. */
export const PRIVATE_PAGE_PREFIXES = ["/studio", "/dev"] as const;
export const PRIVATE_API_PREFIXES = [
  "/api/studio",
  "/api/v1/factory",
  "/api/v1/scheduler",
  "/api/v1/queue",
  "/api/v1/local",
] as const;
export const PRIVATE_PREFIXES = [...PRIVATE_PAGE_PREFIXES, ...PRIVATE_API_PREFIXES] as const;
