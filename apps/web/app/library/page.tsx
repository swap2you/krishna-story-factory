import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import { CollectionCard } from "@/components/collection-card";
import { getCollections, getStories, searchStories } from "@/lib/catalog";
import { StoryGrid } from "@/components/story-grid";
import { brandSrc, brandSrcSet } from "@/lib/brand-assets";
import { getCollectionStatus } from "@/lib/collection-readiness";
import { PUBLIC_STORY_MAX } from "@/lib/public-boundary";

export const dynamic = "force-dynamic";

const storyCeiling = String(PUBLIC_STORY_MAX).padStart(3, "0");

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
      description:
        collections[0]?.description ??
        `Stories 001–${storyCeiling} indexed and ready.`,
      status: getCollectionStatus("krishna-book"),
    },
    {
      href: "/library/srimad-bhagavatam",
      slug: "srimad-bhagavatam",
      title: "Śrīmad-Bhāgavatam",
      description: "Cantos 1–12 — taxonomy prepared; stories not released yet.",
      status: getCollectionStatus("srimad-bhagavatam"),
    },
    {
      href: "/library/bhagavad-gita",
      slug: "bhagavad-gita",
      title: "Bhagavad-gītā",
      description: "Planned verse-by-verse stories for young listeners.",
      status: getCollectionStatus("bhagavad-gita"),
    },
    {
      href: "/library/ramayana",
      slug: "ramayana",
      title: "Rāmāyaṇa",
      description: "Planned retelling of Lord Rāma’s journey for families.",
      status: getCollectionStatus("ramayana"),
    },
    {
      href: "/library/rama-katha",
      slug: "rama-katha",
      title: "Rāma-kathā",
      description: "Planned supplementary Rāma narrations.",
      status: getCollectionStatus("rama-katha"),
    },
    {
      href: "/library/ramacaritamanasa",
      slug: "ramacaritamanasa",
      title: "Rāmacaritamānasa",
      description: "Planned Tulasīdāsa retelling adapted for children.",
      status: getCollectionStatus("ramacaritamanasa"),
    },
    {
      href: "/library/dasavatara",
      slug: "dasavatara",
      title: "Daśāvatāra",
      description: "Planned ten avatāras of Lord Viṣṇu in story form.",
      status: getCollectionStatus("dasavatara"),
    },
    {
      href: "/library/caitanya-caritamrta",
      slug: "caitanya-caritamrta",
      title: "Caitanya-caritāmṛta",
      description: "Planned life and teachings of Śrī Caitanya Mahāprabhu.",
      status: getCollectionStatus("caitanya-caritamrta"),
    },
    {
      href: "/library/caitanya-bhagavata",
      slug: "caitanya-bhagavata",
      title: "Caitanya-bhāgavata",
      description: "Planned account for young readers — not published yet.",
      status: getCollectionStatus("caitanya-bhagavata"),
    },
    {
      href: "/library/prayers-mantras",
      slug: "prayers-mantras",
      title: "Prayers & Mantras",
      description: "Planned morning prayers, key ślokas, and daily mantras.",
      status: getCollectionStatus("prayers-mantras"),
    },
    {
      href: "/library/teacher-resources",
      slug: "teacher-resources",
      title: "Teacher Resources",
      description: "Planned lesson outlines and classroom helpers.",
      status: getCollectionStatus("teacher-resources"),
    },
    {
      href: "/knowledge",
      slug: "knowledge",
      title: "Bhāva Knowledge Library",
      description: "Source-led articles, Q&A, and practice pathways.",
      status: getCollectionStatus("knowledge"),
    },
  ];

  const available = cards.filter((card) => card.status === "active");
  const planned = cards.filter((card) => card.status !== "active");

  return (
    <>
      <PageIntro
        eyebrow="Scripture library"
        title="A growing home for Krishna Book and beyond."
        body={`Browse Stories 001–${storyCeiling} now. Future collections for Bhāgavatam, Rāmāyaṇa, and Caitanya literature appear as Planned shelves — not as published downloads.`}
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

          <h2 className="section-heading" style={{ marginTop: "2rem" }}>
            Available now
          </h2>
          <p className="section-lead">
            Published shelves with real packages or approved Knowledge pages.
          </p>
          <div className="collection-grid-full" data-testid="library-available-shelves">
            {available.map((card) => (
              <CollectionCard key={card.href} {...card} interactive />
            ))}
          </div>

          <h2 className="section-heading" style={{ marginTop: "2.5rem" }}>
            Planned shelves
          </h2>
          <p className="section-lead">
            Taxonomy and coming-soon structure only — not clickable as published content, and with no fake downloads.
          </p>
          <div className="collection-grid-full" data-testid="library-planned-shelves">
            {planned.map((card) => (
              <CollectionCard key={card.href} {...card} interactive={false} />
            ))}
          </div>

          <div style={{ marginTop: "2.5rem" }}>
            <h2 className="section-heading">Released stories</h2>
            <p className="hint" style={{ marginBottom: "1rem" }}>
              Public ceiling: Stories 001–{storyCeiling}. Later numbers stay private until released.
            </p>
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
