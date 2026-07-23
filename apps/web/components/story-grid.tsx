import Link from "next/link";
import { EmptyState } from "@bhava/ui";
import type { Story } from "@/lib/catalog";

export function StoryGrid({
  stories,
  empty = "Stories will appear here as the local catalog becomes available.",
}: {
  stories: Story[];
  empty?: string;
}) {
  if (!stories.length) {
    return (
      <EmptyState title="The library is being prepared">
        <p>{empty}</p>
      </EmptyState>
    );
  }

  return (
    <div className="story-grid">
      {stories.map((story, index) => (
        <article key={story.story_no} className="bhava-card story-card" style={{ animationDelay: `${index * 40}ms` }}>
          <Link href={`/stories/${story.story_no}`} className="story-card-link">
            <div className="story-card-media">
              {story.poster_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={story.poster_url} alt="" />
              ) : null}
              <span className="story-chip">{story.story_no}</span>
            </div>
            <div className="story-card-body">
              <p className="story-no">Krishna Book</p>
              <h3>{story.title}</h3>
              <p>{story.age_range ? `For ${story.age_range}` : "Listen · Read · Color · Learn"}</p>
            </div>
          </Link>
        </article>
      ))}
    </div>
  );
}
