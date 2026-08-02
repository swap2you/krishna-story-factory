import Link from "next/link";
import { CollectionCard } from "@/components/collection-card";
import { loadStories } from "@/lib/catalog";
import { StoryGrid } from "@/components/story-grid";

export const dynamic = "force-dynamic";

const audiences = [
  { title: "Little Listeners", ages: "ages 5–7", body: "Gentle stories, simple coloring, and short listen-alongs." },
  { title: "Young Explorers", ages: "ages 8–12", body: "Richer Krishna Book chapters, activities, and family discussion." },
  { title: "Teen Seekers", ages: "ages 13–15", body: "Scripture pathways, questions, and honest coming-soon learning routes." },
  { title: "Youth Leaders", ages: "ages 16–20", body: "Teacher-ready packs, preaching outlines, and leadership practice." },
  { title: "Families & Educators", ages: "homes & classrooms", body: "Printables, Sunday School planning, and reviewed source notes." },
];

/** Core areas use Library collection-card pattern (art + dark scrim) — never white text on transparent cream. */
const areas = [
  {
    href: "/library/krishna-book",
    slug: "krishna-book",
    title: "Krishna Book Stories",
    description: "Published bedtime packages with audio and printables.",
    status: "active" as const,
  },
  {
    href: "/knowledge",
    slug: "knowledge",
    title: "Knowledge Library",
    description: "Governed pathways, questions, and reviewed guides.",
    status: "active" as const,
  },
  {
    href: "/library/prayers-mantras",
    slug: "prayers-mantras",
    title: "Prayers & Ślokas",
    description: "Public prayer and mantra learning spaces.",
    status: "active" as const,
  },
  {
    href: "/sunday-school",
    slug: "sunday-school",
    title: "Sunday School",
    description: "Weekly planning structure for age groups.",
    status: "planned" as const,
  },
  {
    href: "/teachers",
    slug: "teacher-resources",
    title: "Teacher Resources",
    description: "Class packs and classroom pathways.",
    status: "planned" as const,
  },
  {
    href: "/printables",
    slug: "printables",
    title: "Printables",
    description: "Posters, coloring, and activity sheets from real packages.",
    status: "active" as const,
  },
  {
    href: "/prabhupada-vani",
    slug: "prabhupada-vani",
    title: "Prabhupāda Vāṇī",
    description: "Source-governed taxonomy for future reviewed records.",
    status: "planned" as const,
  },
  {
    href: "/library",
    slug: "devotee-lives",
    title: "Devotee Lives",
    description: "Bhaktamāla / lives of devotees — planned with care.",
    status: "planned" as const,
  },
];

export default async function Home() {
  const state = await loadStories();
  const stories = state.status === "ok" ? state.stories : [];
  const catalogUnavailable = state.status === "unavailable";
  const latest = stories.slice(-3).reverse();
  const featured = stories.find((story) => story.story_no === "001") ?? stories.find((story) => story.poster_url) ?? stories[0];
  const latestStory = stories[stories.length - 1];

  return (
    <>
      <section className="hero hero--platform">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          className="hero-bg"
          src="/heroes/hero-desktop-wide.webp"
          alt=""
          width={1920}
          height={1080}
          aria-hidden="true"
          fetchPriority="high"
          decoding="async"
        />
        <div className="container hero-platform-copy">
          <p className="brand-kicker brand-display">Bhāva</p>
          <h1>Timeless devotion for growing hearts and minds.</h1>
          <p className="hero-copy-text">
            Start with Krishna Book bedtime stories — listen, read, color, and print — while Knowledge and classroom libraries grow with honest planned labels.
          </p>
          <div className="actions" data-testid="home-story-primary-ctas">
            <Link className="bhava-button bhava-button--accent" href="/library/krishna-book">
              Start the Stories
            </Link>
            {latestStory ? (
              <Link className="bhava-button bhava-button--quiet" href={`/stories/${latestStory.story_no}`}>
                Listen to the Latest Story
              </Link>
            ) : null}
            <Link className="bhava-button bhava-button--quiet" href="/printables">
              Browse Activities
            </Link>
            <Link className="bhava-button bhava-button--quiet" href="/printables">
              Print Coloring &amp; Worksheets
            </Link>
          </div>
          <div className="actions actions--secondary">
            <Link className="bhava-button bhava-button--quiet" href="/library">Explore the Library</Link>
            <Link className="bhava-button bhava-button--quiet" href="/knowledge">Browse Knowledge</Link>
            <Link className="bhava-button bhava-button--quiet" href="/learning/children-youth">Start Learning</Link>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <p className="eyebrow">Who Bhāva serves</p>
          <h2 className="section-heading">Age-aware pathways without infantilizing anyone</h2>
          <div className="audience-grid">
            {audiences.map((item) => (
              <article key={item.title} className="audience-card">
                <h3>{item.title}</h3>
                <p className="hint">{item.ages}</p>
                <p>{item.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <p className="eyebrow">Core areas</p>
          <h2 className="section-heading">A complete devotional learning platform</h2>
          <div className="collection-grid" data-testid="home-core-areas">
            {areas.map((card) => (
              <CollectionCard key={card.href + card.title} {...card} />
            ))}
          </div>
        </div>
      </section>

      {featured ? (
        <section className="section featured-story-section">
          <div className="container featured-story">
            <div>
              <p className="eyebrow">Featured story</p>
              <h2 className="section-heading">{featured.title}</h2>
              <p className="section-lead">
                Preserve the dramatic Krishna Book artwork as a featured release — not as the entire platform identity.
              </p>
              <Link className="bhava-button bhava-button--accent" href={`/stories/${featured.story_no}`}>
                Open Story {featured.story_no}
              </Link>
            </div>
            {featured.poster_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={featured.poster_url} alt={`${featured.title} story poster`} width={720} height={900} />
            ) : null}
          </div>
        </section>
      ) : null}

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <p className="eyebrow">Latest releases</p>
          <h2 className="section-heading">Published stories appear automatically</h2>
          <p className="section-lead">
            Curated, source-reviewed, age-aware packages. No child accounts. Unreviewed sacred text is never published.
          </p>
          <StoryGrid
            stories={latest.length ? latest : stories}
            unavailable={catalogUnavailable}
            empty="Published stories will appear here when the catalog is ready."
          />
        </div>
      </section>
    </>
  );
}
