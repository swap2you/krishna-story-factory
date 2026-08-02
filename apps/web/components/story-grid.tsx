import Link from "next/link";
import { EmptyState } from "@bhava/ui";
import type { Story } from "@/lib/catalog";
import { PUBLIC_LIBRARY_UNAVAILABLE } from "@/lib/catalog";

export function CatalogUnavailable({
  message = PUBLIC_LIBRARY_UNAVAILABLE,
}: {
  message?: string;
}) {
  return (
    <EmptyState title="The story library is temporarily unavailable">
      <p>{message}</p>
    </EmptyState>
  );
}

export function StoryGrid({
  stories,
  empty = "Published stories will appear here when the catalog is ready.",
  unavailable = false,
}: {
  stories: Story[];
  empty?: string;
  /** True when the catalog API failed (timeout/network/5xx), not a successful empty list. */
  unavailable?: boolean;
}) {
  if (unavailable) {
    return <CatalogUnavailable />;
  }
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
                <img src={story.poster_url} alt={`${story.title} story poster`} />
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
