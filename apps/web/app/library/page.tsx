import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import { CollectionCard } from "@/components/collection-card";
import { getCollections, getStories, searchStories } from "@/lib/catalog";
import { StoryGrid } from "@/components/story-grid";
import { brandSrc, brandSrcSet } from "@/lib/brand-assets";

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

  const cards = [
    {
      href: "/library/krishna-book",
      slug: "krishna-book",
      title: collections[0]?.title ?? "Krishna Book Bedtime Stories",
      description: collections[0]?.description ?? `${stories.length || 7} stories indexed and ready.`,
      status: "active" as const,
    },
    {
      href: "/library/srimad-bhagavatam",
      slug: "srimad-bhagavatam",
      title: "Śrīmad-Bhāgavatam",
      description: "Cantos 1–12 — coming soon with editorial care.",
    },
    {
      href: "/library/bhagavad-gita",
      slug: "bhagavad-gita",
      title: "Bhagavad-gītā",
      description: "Verse-by-verse stories for young listeners.",
    },
    {
      href: "/library/ramayana",
      slug: "ramayana",
      title: "Rāmāyaṇa",
      description: "The journey of Lord Rāma retold for families.",
    },
    {
      href: "/library/rama-katha",
      slug: "rama-katha",
      title: "Rāma-kathā",
      description: "Supplementary Rāma narrations from Purāṇic sources.",
    },
    {
      href: "/library/ramacaritamanasa",
      slug: "ramacaritamanasa",
      title: "Rāmacaritamānasa",
      description: "Tulasīdāsa's retelling, adapted for children.",
    },
    {
      href: "/library/dasavatara",
      slug: "dasavatara",
      title: "Daśāvatāra",
      description: "Ten avatāras of Lord Viṣṇu in story form.",
    },
    {
      href: "/library/caitanya-caritamrta",
      slug: "caitanya-caritamrta",
      title: "Caitanya-caritāmṛta",
      description: "The life and teachings of Śrī Caitanya Mahāprabhu.",
    },
    {
      href: "/library/caitanya-bhagavata",
      slug: "caitanya-bhagavata",
      title: "Caitanya-bhāgavata",
      description: "Vṛndāvana Dāsa Ṭhākura's account for young readers.",
    },
    {
      href: "/library/prayers-mantras",
      slug: "prayers-mantras",
      title: "Prayers & Mantras",
      description: "Morning prayers, key ślokas, and daily mantras.",
    },
    {
      href: "/library/teacher-resources",
      slug: "teacher-resources",
      title: "Teacher Resources",
      description: "Lesson outlines and classroom helpers.",
    },
    {
      href: "/knowledge",
      slug: "knowledge",
      title: "Bhāva Knowledge Library",
      description: "Curated articles, Q&A, and practice pathways.",
    },
  ];

  return (
    <>
      <PageIntro
        eyebrow="Scripture library"
        title="A growing home for Krishna Book and beyond."
        body="Browse released bedtime stories now. Future collections for Bhāgavatam, Rāmāyaṇa, and Caitanya literature wait as calm coming-soon shelves."
        heroSrc={brandSrc("hero-krishna-book-collection")}
        heroSrcSet={brandSrcSet("hero-krishna-book-collection")}
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
            {cards.map((card) => (
              <CollectionCard key={card.href} {...card} />
            ))}
          </div>

          <div style={{ marginTop: "2.5rem" }}>
            <h2 className="section-heading">Released stories</h2>
            <StoryGrid stories={stories} />
            <p className="hint" style={{ marginTop: "1rem" }}>
              Looking for printables? Visit the <Link href="/printables">Printables hub</Link>.
            </p>
          </div>
        </div>
      </section>
    </>
  );
}
