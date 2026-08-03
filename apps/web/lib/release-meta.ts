/** Build-time release metadata for public footer / SEO (never secrets). */
export type BhavaReleaseMeta = {
  webVersion: string;
  contentRelease: string;
  gitSha: string;
  shortSha: string;
};

function shortSha(sha: string): string {
  const cleaned = sha.trim();
  if (!cleaned || cleaned === "development") return "dev";
  return cleaned.slice(0, 7);
}

export function getBhavaReleaseMeta(): BhavaReleaseMeta {
  const webVersion =
    process.env.NEXT_PUBLIC_BHAVA_WEB_VERSION?.trim() ||
    process.env.BHAVA_WEB_VERSION?.trim() ||
    "0.0.0-dev";
  const contentRelease =
    process.env.NEXT_PUBLIC_BHAVA_CONTENT_RELEASE?.trim() ||
    process.env.BHAVA_CONTENT_RELEASE?.trim() ||
    "bhava-content-001-020-v3";
  const gitSha =
    process.env.NEXT_PUBLIC_BHAVA_GIT_SHA?.trim() ||
    process.env.BHAVA_RELEASE_SHA?.trim() ||
    "development";
  return {
    webVersion,
    contentRelease,
    gitSha,
    shortSha: shortSha(gitSha),
  };
}

export function formatFooterReleaseLine(meta: BhavaReleaseMeta = getBhavaReleaseMeta()): string {
  const contentLabel = meta.contentRelease.replace(/^bhava-content-/, "Content ").replace(/-/g, " ");
  return `Bhāva Web ${meta.webVersion} · ${contentLabel} · Build ${meta.shortSha}`;
}
