import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import { getCollections, getStories, searchStories } from "@/lib/catalog";
import { StoryGrid } from "@/components/story-grid";

export default async function LibraryPage({
  searchParams,
}: {
  searchParams?: Promise<{ q?: string }>;
}) {
  const params = searchParams ? await searchParams : {};
  const query = params.q ?? "";
  const [stories, collections] = await Promise.all([
    query ? searchStories(query) : getStories(),
    getCollections(),
  ]);

  return (
    <>
      <PageIntro
        eyebrow="Scripture library"
        title="A growing home for Krishna Book and beyond."
        body="Browse released bedtime stories now. Future collections for Bhāgavatam, Rāmāyaṇa, and Caitanya literature wait as calm coming-soon shelves."
      />
      <section className="section">
        <div className="container">
          <form className="actions" action="/library" method="get">
            <label className="sr-only" htmlFor="library-search">Search stories</label>
            <input
              id="library-search"
              name="q"
              defaultValue={query}
              placeholder="Search by title, chapter, or source"
              style={{ minHeight: 44, minWidth: 260, padding: "0.6rem 0.9rem", borderRadius: 12, border: "1px solid var(--bhava-border)" }}
            />
            <button className="bhava-button bhava-button--primary" type="submit">Search</button>
          </form>
          <div className="story-grid" style={{ marginTop: "2rem" }}>
            {(collections.length ? collections : [{ slug: "krishna-book-bedtime", title: "Krishna Book Bedtime Stories", description: "Stories 001–007", story_count: stories.length }]).map((collection) => (
              <Link key={collection.slug} href="/library/krishna-book" className="story-card bhava-card">
                <p className="story-no">Collection</p>
                <h3>{collection.title}</h3>
                <p>{collection.description}</p>
                <p>{collection.story_count ?? stories.length} stories indexed</p>
              </Link>
            ))}
            <div className="story-card bhava-card">
              <p className="story-no">Coming soon</p>
              <h3>Śrīmad-Bhāgavatam Cantos 1–12</h3>
              <p>Structure ready. Content not yet curated.</p>
            </div>
            <div className="story-card bhava-card">
              <p className="story-no">Coming soon</p>
              <h3>Rāmāyaṇa & Caitanya literature</h3>
              <p>Shelves reserved without invented titles.</p>
            </div>
          </div>
          <h2 className="section-heading" style={{ marginTop: "3rem" }}>Latest Krishna Book stories</h2>
          <StoryGrid stories={stories} empty="Start the local API to index Stories 001–007 from your packages." />
        </div>
      </section>
    </>
  );
}
