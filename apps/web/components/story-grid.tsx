import Link from "next/link";
import { Card, EmptyState } from "@bhava/ui";
import type { Story } from "@/lib/catalog";

export function StoryGrid({ stories }: { stories: Story[] }) {
  if (!stories.length) return <EmptyState title="The library is being prepared"><p>Stories will appear here as the local catalog becomes available.</p></EmptyState>;
  return <div className="story-grid">{stories.map((story) => <Card key={story.story_no} className="story-card"><Link href={`/stories/${story.story_no}`}><p className="story-no">KRISHNA BOOK · {story.story_no}</p><h3>{story.title}</h3><p>{story.age_range ? `For ${story.age_range}` : "Open a gentle reading experience"}</p></Link></Card>)}</div>;
}
