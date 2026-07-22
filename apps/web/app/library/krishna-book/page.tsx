import { getStories, type Story } from "@/lib/catalog";
import { StoryGrid } from "@/components/story-grid";

export default async function KrishnaBookPage() {
  let stories: Story[] = [];
  try { stories = await getStories(); } catch { /* catalog is optional for this shell */ }
  return <><section className="page-hero"><div className="container"><p className="eyebrow">The Krishna Book</p><h1>A sequence of divine childhood pastimes.</h1><p>Each story is shared in order, with listening, reading, activities, and source notes.</p></div></section><section className="section"><div className="container"><StoryGrid stories={stories} /></div></section></>;
}
