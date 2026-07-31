import { PageIntro } from "@/components/page-intro";
import { StoryGrid } from "@/components/story-grid";
import { getStories } from "@/lib/catalog";
import { pageMetadata } from "@/lib/seo";

export const dynamic = "force-dynamic";

export const metadata = pageMetadata({
  title: "Krishna Book stories for children",
  description:
    "Published Krishna Book bedtime packages with audio, activities, coloring pages and teacher-ready printables.",
  path: "/library/krishna-book",
});

function publishedRangeLabel(storyNos: string[]): string {
  const nums = storyNos
    .map((n) => Number.parseInt(String(n || ""), 10))
    .filter((n) => Number.isFinite(n) && n > 0)
    .sort((a, b) => a - b);
  if (!nums.length) return "published Krishna Book stories";
  const first = String(nums[0]).padStart(3, "0");
  const last = String(nums[nums.length - 1]).padStart(3, "0");
  if (first === last) return `Story ${first}`;
  return `Stories ${first}–${last}`;
}

export default async function KrishnaBookPage() {
  const stories = await getStories();
  const range = publishedRangeLabel(stories.map((s) => s.story_no));
  return (
    <>
      <PageIntro
        eyebrow="Krishna Book"
        title={`Chapter timeline for ${range}.`}
        body="Each card opens listening, reading, activities, coloring, source references, and device-local notes. Incomplete factory packages stay out of this list until they pass the exact-eight publish gate."
      />
      <section className="section">
        <div className="container">
          <StoryGrid stories={stories} empty="Run the Bhāva API so the catalog can discover locked packages." />
        </div>
      </section>
    </>
  );
}
