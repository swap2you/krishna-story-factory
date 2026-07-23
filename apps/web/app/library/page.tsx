import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import { getCollections, getStories, searchStories } from "@/lib/catalog";
import { StoryGrid } from "@/components/story-grid";

export const dynamic = "force-dynamic";

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
          <form className="search-bar" action="/library" method="get">
            <label className="sr-only" htmlFor="library-search">Search stories</label>
            <input
              id="library-search"
              name="q"
              defaultValue={query}
              placeholder="Search by title, chapter, or source"
            />
            <button className="bhava-button bhava-button--primary" type="submit">Search</button>
          </form>

          <div className="collection-grid" style={{ marginTop: "2rem" }}>
            <Link href="/library/krishna-book" className="collection-card krishna">
              <h3>{collections[0]?.title ?? "Krishna Book Bedtime Stories"}</h3>
              <p>{collections[0]?.description ?? `${stories.length || 7} stories indexed and ready.`}</p>
              <span className="orb" aria-hidden="true" />
            </Link>
            <div className="collection-card lotus">
              <h3>Śrīmad-Bhāgavatam</h3>
              <p>Cantos 1–12 — coming soon with editorial care.</p>
              <span className="orb" aria-hidden="true" />
            </div>
            <div className="collection-card forest">
              <h3>Rāmāyaṇa & Caitanya</h3>
              <p>Shelves reserved without invented titles.</p>
              <span className="orb" aria-hidden="true" />
            </div>
          </div>

          <h2 className="section-heading" style={{ marginTop: "3rem" }}>
            {query ? `Results for “${query}”` : "Latest Krishna Book stories"}
          </h2>
          <StoryGrid stories={stories} empty="Start the local API so the catalog can discover Stories 001–007." />
        </div>
      </section>
    </>
  );
}
