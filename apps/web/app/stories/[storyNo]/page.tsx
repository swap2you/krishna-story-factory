import Link from "next/link";
import { notFound } from "next/navigation";
import { getStory } from "@/lib/catalog";
import { StoryExperience } from "@/components/story-experience";

export default async function StoryPage({ params }: { params: Promise<{ storyNo: string }> }) {
  const { storyNo } = await params;
  if (!/^[a-z0-9-]+$/i.test(storyNo)) notFound();
  let story = null;
  try {
    story = await getStory(storyNo);
  } catch {
    /* shell remains available without API */
  }

  return (
    <div className="story-shell">
      <aside className="story-sidebar">
        <Link href="/library/krishna-book" className="bhava-button bhava-button--quiet" style={{ color: "#fff", borderColor: "rgba(255,255,255,.25)" }}>
          ← Krishna Book
        </Link>
        {story?.poster_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={story.poster_url} alt="" />
        ) : (
          <div style={{ aspectRatio: "1", margin: "1rem 0", borderRadius: "1.15rem", background: "linear-gradient(145deg,#1a3354,#6a3a4a)" }} />
        )}
        <p className="source-pill">Story {story?.story_no ?? storyNo}</p>
        <h2>{story?.title ?? "A story in preparation"}</h2>
        <p>{story?.age_range ? `Suggested for ${story.age_range}` : "A gentle Radha-Krishna bedtime experience."}</p>
        <p>{story?.source_reference ?? "Source references appear when the catalog is connected."}</p>
      </aside>
      <section className="story-main">
        <div className="story-top">
          <div>
            <p className="eyebrow">Listen · Read · Activities</p>
            <h1>{story?.title ?? "A story in preparation"}</h1>
          </div>
          <span className="status-chip">{story?.quality_status ?? "Catalog"}</span>
        </div>
        <StoryExperience story={story} storyNo={story?.story_no ?? storyNo} />
      </section>
    </div>
  );
}
