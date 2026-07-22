export type Story = {
  story_no: string;
  slug: string;
  title: string;
  source_reference?: string | null;
  scripture_reference?: string | null;
  age_range?: string | null;
  summary?: string | null;
  narration_url?: string | null;
  activity_pdf_url?: string | null;
  images?: string[];
};

const API = process.env.BHAVA_API_URL ?? "http://127.0.0.1:8000/api/v1";

export async function getStories(): Promise<Story[]> {
  const response = await fetch(`${API}/stories`, { signal: AbortSignal.timeout(2500) });
  if (!response.ok) throw new Error(`Catalog request failed (${response.status})`);
  const body = await response.json();
  return Array.isArray(body) ? body : body.items ?? body.stories ?? [];
}

export async function getStory(storyNo: string): Promise<Story | null> {
  const stories = await getStories();
  return stories.find((story) => story.story_no === storyNo || story.slug === storyNo) ?? null;
}
