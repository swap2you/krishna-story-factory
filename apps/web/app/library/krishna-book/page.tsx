import { PageIntro } from "@/components/page-intro";
import { StoryGrid } from "@/components/story-grid";
import { getStories } from "@/lib/catalog";

export default async function KrishnaBookPage() {
  const stories = await getStories();
  return (
    <>
      <PageIntro
        eyebrow="Krishna Book"
        title="Chapter timeline for Stories 001–007."
        body="Each card opens listening, reading, activities, coloring, source references, and device-local notes. Story 008 stays pending in the factory queue and is not listed until released."
      />
      <section className="section">
        <div className="container">
          <ol className="story-grid" style={{ listStyle: "none", padding: 0, margin: 0 }}>
            <StoryGrid stories={stories} empty="Run the Bhāva API so the catalog can discover locked packages." />
          </ol>
        </div>
      </section>
    </>
  );
}
