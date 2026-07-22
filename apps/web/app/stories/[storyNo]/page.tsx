import { notFound } from "next/navigation";
import { getStory } from "@/lib/catalog";
import { StoryExperience } from "@/components/story-experience";

export default async function StoryPage({ params }: { params: Promise<{ storyNo: string }> }) {
  const { storyNo } = await params;
  if (!/^[a-z0-9-]+$/i.test(storyNo)) notFound();
  let story = null;
  try { story = await getStory(storyNo); } catch { /* shell remains available without API */ }
  return <div className="container story-layout"><section><p className="eyebrow">Krishna Book · {storyNo}</p><h1>{story?.title ?? "A story in preparation"}</h1><StoryExperience story={story} storyNo={storyNo} /></section><aside className="story-aside"><h2>At a glance</h2><p>{story?.age_range ? `For ${story.age_range}` : "A gentle devotional story experience."}</p><p>Local catalog data is used whenever it is available.</p></aside></div>;
}
