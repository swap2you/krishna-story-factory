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

          <div className="collection-grid-full" style={{ marginTop: "2rem" }}>
            <Link href="/library/krishna-book" className="collection-card krishna">
              <h3>{collections[0]?.title ?? "Krishna Book Bedtime Stories"}</h3>
              <p>{collections[0]?.description ?? `${stories.length || 7} stories indexed and ready.`}</p>
              <span className="editorial-status active">Active</span>
              <span className="orb" aria-hidden="true" />
            </Link>
            <Link href="/library/srimad-bhagavatam" className="collection-card lotus">
              <h3>Śrīmad-Bhāgavatam</h3>
              <p>Cantos 1–12 — coming soon with editorial care.</p>
              <span className="editorial-status planned">Planned</span>
              <span className="orb" aria-hidden="true" />
            </Link>
            <Link href="/library/bhagavad-gita" className="collection-card gita">
              <h3>Bhagavad-gītā</h3>
              <p>Verse-by-verse stories for young listeners.</p>
              <span className="editorial-status planned">Planned</span>
              <span className="orb" aria-hidden="true" />
            </Link>
            <Link href="/library/ramayana" className="collection-card forest">
              <h3>Rāmāyaṇa</h3>
              <p>The journey of Lord Rāma retold for families.</p>
              <span className="editorial-status planned">Planned</span>
              <span className="orb" aria-hidden="true" />
            </Link>
            <Link href="/library/rama-katha" className="collection-card rama">
              <h3>Rāma-kathā</h3>
              <p>Supplementary Rāma narrations from Purāṇic sources.</p>
              <span className="editorial-status planned">Planned</span>
              <span className="orb" aria-hidden="true" />
            </Link>
            <Link href="/library/ramacaritamanasa" className="collection-card manasa">
              <h3>Rāmacaritamānasa</h3>
              <p>Tulasīdāsa's retelling, adapted for children.</p>
              <span className="editorial-status planned">Planned</span>
              <span className="orb" aria-hidden="true" />
            </Link>
            <Link href="/library/dasavatara" className="collection-card avatar">
              <h3>Daśāvatāra</h3>
              <p>Ten avatāras of Lord Viṣṇu in story form.</p>
              <span className="editorial-status planned">Planned</span>
              <span className="orb" aria-hidden="true" />
            </Link>
            <Link href="/library/caitanya-caritamrta" className="collection-card amber">
              <h3>Caitanya-caritāmṛta</h3>
              <p>The life and teachings of Śrī Caitanya Mahāprabhu.</p>
              <span className="editorial-status planned">Planned</span>
              <span className="orb" aria-hidden="true" />
            </Link>
            <Link href="/library/caitanya-bhagavata" className="collection-card rose">
              <h3>Caitanya-bhāgavata</h3>
              <p>Vṛndāvana Dāsa Ṭhākura's account for young readers.</p>
              <span className="editorial-status planned">Planned</span>
              <span className="orb" aria-hidden="true" />
            </Link>
            <Link href="/library/prayers-mantras" className="collection-card indigo">
              <h3>Prayers &amp; Mantras</h3>
              <p>Morning prayers, key ślokas, and daily mantras.</p>
              <span className="editorial-status planned">Planned</span>
              <span className="orb" aria-hidden="true" />
            </Link>
            <Link href="/library/teacher-resources" className="collection-card earth">
              <h3>Teacher Resources</h3>
              <p>Curriculum guides and classroom materials.</p>
              <span className="editorial-status planned">Planned</span>
              <span className="orb" aria-hidden="true" />
            </Link>
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
