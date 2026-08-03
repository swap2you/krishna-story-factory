import Link from "next/link";
import { CollectionCard } from "@/components/collection-card";
import { loadStories } from "@/lib/catalog";
import { StoryGrid } from "@/components/story-grid";

export const dynamic = "force-dynamic";

const audiences = [
  { title: "Little Listeners", ages: "5–7" },
  { title: "Young Explorers", ages: "8–12" },
  { title: "Teen Seekers", ages: "13–15" },
  { title: "Youth Leaders", ages: "16–20" },
  { title: "Families & Educators", ages: "homes & classrooms" },
];

const journeySteps = [
  { title: "Listen", body: "Bedtime narration with a calm pace." },
  { title: "Read", body: "The same canonical story text." },
  { title: "Create", body: "Coloring pages and activity sheets." },
  { title: "Read the source", body: "Reviewed Krishna Book & Vedabase links." },
  { title: "Reflect and share", body: "Family notes and gentle discussion." },
];

const activeAreas = [
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
    href: "/printables",
    slug: "printables",
    title: "Printables",
    description: "Posters, coloring, and activity sheets from real packages.",
    status: "active" as const,
  },
];

const growingNext = [
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
  const previousStory =
    latestStory && stories.length > 1
      ? stories[stories.length - 2]
      : null;

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
            One calm weekly journey: listen tonight, read and create tomorrow, then return to the reviewed source.
          </p>
          <div className="actions" data-testid="home-story-primary-ctas">
            <Link className="bhava-button bhava-button--accent" href="/library/krishna-book">
              Begin the Krishna Story Journey
            </Link>
            {latestStory ? (
              <Link className="bhava-button bhava-button--quiet" href={`/stories/${latestStory.story_no}`}>
                Continue with Story {latestStory.story_no}
              </Link>
            ) : null}
          </div>
          <p className="hero-text-link">
            <Link href="/library/krishna-book/how-to-use">See how the weekly story journey works</Link>
          </p>
        </div>
      </section>

      {latestStory ? (
        <section className="section continue-journey" aria-labelledby="continue-journey-heading">
          <div className="container continue-journey-card">
            <div>
              <p className="eyebrow">Continue the journey</p>
              <h2 id="continue-journey-heading" className="section-heading">
                Story {latestStory.story_no}: {latestStory.title}
              </h2>
              <p className="section-lead">
                {previousStory
                  ? `After Story ${previousStory.story_no}, keep the rhythm with tonight’s listen and tomorrow’s create time.`
                  : "Keep a gentle weekly rhythm with listening, reading, and creating."}
              </p>
              <div className="actions">
                <Link className="bhava-button bhava-button--accent" href={`/stories/${latestStory.story_no}`}>
                  Listen tonight
                </Link>
                <Link
                  className="bhava-button bhava-button--quiet"
                  href={`/stories/${latestStory.story_no}`}
                >
                  Read and create tomorrow
                </Link>
                <Link className="bhava-button bhava-button--quiet" href="/library/krishna-book/how-to-use">
                  How to use guide
                </Link>
              </div>
            </div>
            {latestStory.poster_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={latestStory.poster_url}
                alt=""
                width={480}
                height={600}
                className="continue-journey-poster"
              />
            ) : null}
          </div>
        </section>
      ) : null}

      <section className="section how-bhava-works" aria-labelledby="how-bhava-works-heading">
        <div className="container">
          <p className="eyebrow">How Bhāva works</p>
          <h2 id="how-bhava-works-heading" className="section-heading">
            Five gentle steps each week
          </h2>
          <ol className="journey-strip">
            {journeySteps.map((step, index) => (
              <li key={step.title} className="journey-strip-step">
                <span className="journey-strip-num" aria-hidden="true">
                  {index + 1}
                </span>
                <JourneyStepIcon step={index} />
                <h3>{step.title}</h3>
                <p>{step.body}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <p className="eyebrow">Explore Bhāva</p>
          <h2 className="section-heading">Start with what is ready today</h2>
          <div className="collection-grid" data-testid="home-core-areas">
            {activeAreas.map((card) => (
              <CollectionCard key={card.href + card.title} {...card} />
            ))}
          </div>

          <details className="growing-next">
            <summary>Growing next</summary>
            <p className="hint">Honest planned destinations — not yet equally ready for every family.</p>
            <div className="collection-grid collection-grid--quiet">
              {growingNext.map((card) => (
                <CollectionCard key={card.href + card.title} {...card} />
              ))}
            </div>
          </details>
        </div>
      </section>

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

      <section className="section audience-compact-section">
        <div className="container">
          <p className="eyebrow">Who Bhāva serves</p>
          <h2 className="section-heading">Age-aware pathways without infantilizing anyone</h2>
          <p className="section-lead">
            Gentle stories for little listeners, richer chapters for explorers, and classroom tools for families and educators.
          </p>
          <ul className="audience-chips" aria-label="Audience pathways">
            {audiences.map((item) => (
              <li key={item.title}>
                <span className="audience-chip">
                  <strong>{item.title}</strong>
                  <span className="hint">{item.ages}</span>
                </span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {featured && featured.story_no !== latestStory?.story_no ? (
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
    </>
  );
}

function JourneyStepIcon({ step }: { step: number }) {
  const common = {
    width: 56,
    height: 56,
    viewBox: "0 0 56 56",
    fill: "none",
    "aria-hidden": true as const,
    className: "journey-strip-icon",
  };
  switch (step) {
    case 0:
      return (
        <svg {...common}>
          <circle cx="28" cy="28" r="22" stroke="#c47a2c" strokeWidth="2.2" strokeDasharray="4 3" />
          <path d="M22 18v20l16-10-16-10z" fill="#e8b84a" stroke="#8a4b12" strokeWidth="1.5" strokeLinejoin="round" />
        </svg>
      );
    case 1:
      return (
        <svg {...common}>
          <rect x="14" y="12" width="28" height="32" rx="4" stroke="#3f6d4f" strokeWidth="2.2" fill="#f7f1e4" />
          <path d="M20 22h16M20 28h14M20 34h10" stroke="#8a6a3a" strokeWidth="2" strokeLinecap="round" />
        </svg>
      );
    case 2:
      return (
        <svg {...common}>
          <path d="M16 38l8-22 8 10 8-16" stroke="#c47a2c" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
          <circle cx="40" cy="14" r="3.5" fill="#e8b84a" stroke="#8a4b12" strokeWidth="1.2" />
        </svg>
      );
    case 3:
      return (
        <svg {...common}>
          <path d="M18 14h20v28H18z" stroke="#12375e" strokeWidth="2.2" fill="#eef3f8" />
          <path d="M22 22h12M22 28h10M22 34h8" stroke="#5a7a9a" strokeWidth="2" strokeLinecap="round" />
        </svg>
      );
    default:
      return (
        <svg {...common}>
          <path
            d="M28 40s-12-7.5-12-16a7 7 0 0 1 12-4 7 7 0 0 1 12 4c0 8.5-12 16-12 16z"
            fill="#f3c9c0"
            stroke="#a14d3a"
            strokeWidth="2"
            strokeLinejoin="round"
          />
        </svg>
      );
  }
}
