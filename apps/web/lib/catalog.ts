export type StoryAsset = {
  filename: string;
  media_type: string;
  url: string;
};

export type Story = {
  story_no: string;
  slug: string;
  title: string;
  source_reference?: string | null;
  scripture_reference?: string | null;
  age_range?: string | null;
  quality_status?: string | null;
  assets?: StoryAsset[];
  summary?: string | null;
  narration_url?: string | null;
  activity_pdf_url?: string | null;
  poster_url?: string | null;
  coloring_url?: string | null;
  simple_coloring_url?: string | null;
  story_md_url?: string | null;
  reader_url?: string | null;
  images?: string[];
};

export type Collection = {
  slug: string;
  title: string;
  description?: string | null;
  story_count?: number;
};

export type CatalogFailureReason = "timeout" | "network" | "http_error" | "invalid_json";

export type CatalogLoadState =
  | { status: "ok"; stories: Story[] }
  | { status: "unavailable"; reason: CatalogFailureReason; httpStatus?: number };

/** Prefer same-origin `/api/...` so Next rewrites avoid browser CORS issues. */
function mediaUrl(url: string | undefined | null): string | null {
  if (!url) return null;
  if (url.startsWith("/")) return url;
  if (url.startsWith("http")) {
    try {
      const parsed = new URL(url);
      if (parsed.hostname === "127.0.0.1" || parsed.hostname === "localhost") {
        return parsed.pathname + parsed.search;
      }
    } catch {
      /* keep original */
    }
    return url;
  }
  return `/${url}`;
}

function enrich(story: Story): Story {
  const byName = Object.fromEntries((story.assets ?? []).map((asset) => [asset.filename, mediaUrl(asset.url)]));
  return {
    ...story,
    narration_url: byName["narration.mp3"] ?? mediaUrl(story.narration_url) ?? null,
    activity_pdf_url: byName["activity_sheet.pdf"] ?? mediaUrl(story.activity_pdf_url) ?? null,
    poster_url: byName["story_poster.png"] ?? mediaUrl(story.poster_url) ?? null,
    coloring_url: byName["coloring_page.png"] ?? mediaUrl(story.coloring_url) ?? null,
    simple_coloring_url: byName["simple_coloring_page.png"] ?? mediaUrl(story.simple_coloring_url) ?? null,
    story_md_url: byName["story.md"] ?? mediaUrl(story.story_md_url) ?? null,
    reader_url: mediaUrl(story.reader_url) ?? `/api/v1/stories/${story.story_no}/reader`,
    images: [
      (byName["story_poster.png"] ?? story.poster_url) ? "Poster" : "",
      (byName["coloring_page.png"] ?? story.coloring_url) ? "Detailed coloring" : "",
      (byName["simple_coloring_page.png"] ?? story.simple_coloring_url) ? "Simple coloring" : "",
    ].filter(Boolean),
  };
}

const API =
  process.env.BHAVA_API_URL ??
  (process.env.BHAVA_API_ORIGIN
    ? `${process.env.BHAVA_API_ORIGIN.replace(/\/$/, "")}/api/v1`
    : "http://127.0.0.1:8000/api/v1");

function logCatalogFailure(path: string, reason: CatalogFailureReason, httpStatus?: number): void {
  // Safe server-side context only — never log internal service URLs or secrets.
  console.error(
    JSON.stringify({
      event: "bhava_catalog_fetch_failed",
      path,
      reason,
      httpStatus: httpStatus ?? null,
    }),
  );
}

async function apiGetRaw(path: string): Promise<
  | { ok: true; data: unknown }
  | { ok: false; reason: CatalogFailureReason; httpStatus?: number }
> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 4000);
  try {
    const response = await fetch(`${API}${path}`, {
      cache: "no-store",
      signal: controller.signal,
    });
    if (!response.ok) {
      return { ok: false, reason: "http_error", httpStatus: response.status };
    }
    try {
      return { ok: true, data: await response.json() };
    } catch {
      return { ok: false, reason: "invalid_json", httpStatus: response.status };
    }
  } catch (error) {
    const name = error instanceof Error ? error.name : "";
    if (name === "AbortError") {
      return { ok: false, reason: "timeout" };
    }
    return { ok: false, reason: "network" };
  } finally {
    clearTimeout(timer);
  }
}

function asStoryList(body: unknown): Story[] {
  if (Array.isArray(body)) return body as Story[];
  if (body && typeof body === "object") {
    const record = body as { items?: Story[]; stories?: Story[] };
    return record.items ?? record.stories ?? [];
  }
  return [];
}

export async function loadStories(): Promise<CatalogLoadState> {
  const result = await apiGetRaw("/stories");
  if (!result.ok) {
    logCatalogFailure("/stories", result.reason, result.httpStatus);
    return { status: "unavailable", reason: result.reason, httpStatus: result.httpStatus };
  }
  return { status: "ok", stories: asStoryList(result.data).map(enrich) };
}

export async function getStories(): Promise<Story[]> {
  const state = await loadStories();
  return state.status === "ok" ? state.stories : [];
}

export async function getStory(storyNo: string): Promise<Story | null> {
  const padded = storyNo.replace(/\D/g, "").padStart(3, "0") || storyNo;
  const result = await apiGetRaw(`/stories/${padded}`);
  if (result.ok && result.data && typeof result.data === "object" && !Array.isArray(result.data)) {
    return enrich(result.data as Story);
  }
  const stories = await getStories();
  return stories.find((item) => item.story_no === padded || item.slug === storyNo) ?? null;
}

export async function getCollections(): Promise<Collection[]> {
  const result = await apiGetRaw("/collections");
  if (!result.ok) {
    logCatalogFailure("/collections", result.reason, result.httpStatus);
    return [];
  }
  return Array.isArray(result.data) ? (result.data as Collection[]) : [];
}

export async function searchStories(query: string): Promise<Story[]> {
  if (!query.trim()) return getStories();
  const result = await apiGetRaw(`/search?q=${encodeURIComponent(query.trim())}`);
  if (!result.ok) {
    logCatalogFailure("/search", result.reason, result.httpStatus);
    return [];
  }
  return asStoryList(result.data).map(enrich);
}

export const PUBLIC_LIBRARY_UNAVAILABLE =
  "The story library is temporarily unavailable. Please try again shortly.";
