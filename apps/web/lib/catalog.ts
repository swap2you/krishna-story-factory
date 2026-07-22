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
  images?: string[];
};

export type Collection = {
  slug: string;
  title: string;
  description?: string | null;
  story_count?: number;
};

const API = process.env.BHAVA_API_URL ?? "http://127.0.0.1:8000/api/v1";

function absUrl(url: string | undefined | null): string | null {
  if (!url) return null;
  if (url.startsWith("http")) return url;
  const origin = process.env.BHAVA_API_ORIGIN ?? "http://127.0.0.1:8000";
  return `${origin}${url}`;
}

function enrich(story: Story): Story {
  const byName = Object.fromEntries((story.assets ?? []).map((asset) => [asset.filename, absUrl(asset.url)]));
  return {
    ...story,
    narration_url: byName["narration.mp3"] ?? story.narration_url ?? null,
    activity_pdf_url: byName["activity_sheet.pdf"] ?? story.activity_pdf_url ?? null,
    poster_url: byName["story_poster.png"] ?? story.poster_url ?? null,
    coloring_url: byName["coloring_page.png"] ?? story.coloring_url ?? null,
    simple_coloring_url: byName["simple_coloring_page.png"] ?? story.simple_coloring_url ?? null,
    story_md_url: byName["story.md"] ?? story.story_md_url ?? null,
    images: [
      byName["story_poster.png"] ? "Poster" : "",
      byName["coloring_page.png"] ? "Detailed coloring" : "",
      byName["simple_coloring_page.png"] ? "Simple coloring" : "",
    ].filter(Boolean),
  };
}

async function apiGet<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${API}${path}`, {
      next: { revalidate: 30 },
      signal: AbortSignal.timeout(4000),
    });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export async function getStories(): Promise<Story[]> {
  const body = await apiGet<Story[] | { items?: Story[]; stories?: Story[] }>("/stories");
  if (!body) return [];
  const list = Array.isArray(body) ? body : body.items ?? body.stories ?? [];
  return list.map(enrich);
}

export async function getStory(storyNo: string): Promise<Story | null> {
  const padded = storyNo.replace(/\D/g, "").padStart(3, "0") || storyNo;
  const story = await apiGet<Story>(`/stories/${padded}`);
  if (story) return enrich(story);
  const stories = await getStories();
  return stories.find((item) => item.story_no === padded || item.slug === storyNo) ?? null;
}

export async function getCollections(): Promise<Collection[]> {
  return (await apiGet<Collection[]>("/collections")) ?? [];
}

export async function searchStories(query: string): Promise<Story[]> {
  if (!query.trim()) return getStories();
  const body = await apiGet<Story[]>(`/search?q=${encodeURIComponent(query.trim())}`);
  return (body ?? []).map(enrich);
}
