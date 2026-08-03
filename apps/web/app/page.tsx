import { CollectionCard } from "@/components/collection-card";
import { loadStories } from "@/lib/catalog";
import { StoryGrid } from "@/components/story-grid";
import { ContinueJourney } from "@/components/continue-journey";
import { AudiencePathwayGrid } from "@/components/audience-pathway-grid";
import { ACTIVE_AREAS, GROWING_NEXT } from "@/lib/collection-readiness";

export const dynamic = "force-dynamic";

const journeySteps = [
  { title: "Listen", body: "Bedtime narration with a calm pace." },
  { title: "Read", body: "The same canonical story text." },
  { title: "Create", body: "Coloring pages and activity sheets." },
  { title: "Read the source", body: "Reviewed Krishna Book & Vedabase links." },
  { title: "Reflect and share", body: "Family notes and gentle discussion." },
];

export default async function Home() {
  const state = await loadStories();
  const stories = state.status === "ok" ? state.stories : [];
  const catalogUnavailable = state.status === "unavailable";
  const latest = stories.slice(-3).reverse();

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
          <ContinueJourney />
        </div>
      </section>

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
          <p className="eyebrow">Latest releases</p>
          <h2 className="section-heading">Continue the Krishna Book journey</h2>
          <p className="section-lead">
            Newly released stories for listening, reading, coloring, and family learning.
          </p>
          <StoryGrid
            stories={latest.length ? latest : stories}
            unavailable={catalogUnavailable}
            empty="Stories will appear here as they are released for families."
          />
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <p className="eyebrow">Explore Bhāva</p>
          <h2 className="section-heading">Start with what is ready today</h2>
          <div className="collection-grid" data-testid="home-core-areas">
            {ACTIVE_AREAS.map((card) => (
              <CollectionCard key={card.href + card.title} {...card} />
            ))}
          </div>
        </div>
      </section>

      <section className="section audience-compact-section">
        <div className="container">
          <p className="eyebrow">Who Bhāva serves</p>
          <h2 className="section-heading">Age-aware pathways without infantilizing anyone</h2>
          <p className="section-lead">
            Educational pathways inspired by traditional age-stage language—used only as learning labels, not as claims about transcendental qualities.
          </p>
          <AudiencePathwayGrid />
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <details className="growing-next">
            <summary>Growing next</summary>
            <p className="hint">Honest planned destinations — not yet equally ready for every family.</p>
            <div className="collection-grid collection-grid--quiet">
              {GROWING_NEXT.map((card) => (
                <CollectionCard key={card.href + card.title} {...card} />
              ))}
            </div>
          </details>
        </div>
      </section>
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
