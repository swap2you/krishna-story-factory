/** Governed public story ceiling. Default matches RELEASE_CONTENT.json production pin. */

function resolvePublicStoryMax(): number {
  const raw =
    process.env.NEXT_PUBLIC_BHAVA_PUBLIC_STORY_MAX ||
    process.env.BHAVA_PUBLIC_STORY_MAX ||
    "25";
  const parsed = Number.parseInt(String(raw).trim(), 10);
  if (!Number.isFinite(parsed) || parsed < 1) {
    return 25;
  }
  return Math.min(parsed, 999);
}

export const PUBLIC_STORY_MAX = resolvePublicStoryMax();
