import Link from "next/link";
import { pageMetadata, CANONICAL_ORIGIN } from "@/lib/seo";

const PAGE_DESCRIPTION =
  "A practical weekly journey: listen tonight, read and color tomorrow, then return to reviewed source and gentle family reflection.";

export const metadata = pageMetadata({
  title: "How to use Krishna Book stories",
  description: PAGE_DESCRIPTION,
  path: "/library/krishna-book/how-to-use",
});

const STEPS = [
  {
    id: "listen",
    title: "Listen tonight",
    body: "Choose the current story, play the bedtime narration, and use the sleep timer if it helps the room settle.",
    href: "/stories/020",
    linkLabel: "Open a story to listen",
  },
  {
    id: "read",
    title: "Read tomorrow",
    body: "Open the Read tab. The words you hear and the words you read come from the same canonical story text.",
    href: "/stories/020",
    linkLabel: "Open the Read experience",
  },
  {
    id: "create",
    title: "Create and color",
    body: "Print the activity sheet, choose simple or detailed coloring, and complete it during the day.",
    href: "/printables",
    linkLabel: "Browse printables",
  },
  {
    id: "source",
    title: "Read the source",
    body: "Open Source and Ślokas. Follow the reviewed Vedabase link. Exact chapter and verse ranges appear only when verified.",
    href: "/stories/020",
    linkLabel: "See a source example",
  },
  {
    id: "reflect",
    title: "Reflect and share",
    body: "Write a private note, discuss the lesson together, and optionally share completed work with family or class. No WhatsApp join link is published until an approved URL exists.",
    href: "/stories/020",
    linkLabel: "Open Notes on a story",
  },
];

export default function HowToUseKrishnaBookPage() {
  const howToJsonLd = {
    "@context": "https://schema.org",
    "@type": "HowTo",
    name: "How to use Krishna Book stories on Bhāva",
    description: PAGE_DESCRIPTION,
    url: `${CANONICAL_ORIGIN}/library/krishna-book/how-to-use`,
    step: STEPS.map((step, index) => ({
      "@type": "HowToStep",
      position: index + 1,
      name: step.title,
      text: step.body,
      url: `${CANONICAL_ORIGIN}${step.href}`,
    })),
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(howToJsonLd) }}
      />

      <section className="section how-to-use">
        <div className="container">
          <nav className="breadcrumb" aria-label="Breadcrumb">
            <Link href="/">Home</Link>
            <span aria-hidden="true"> / </span>
            <Link href="/library">Library</Link>
            <span aria-hidden="true"> / </span>
            <Link href="/library/krishna-book">Krishna Book</Link>
            <span aria-hidden="true"> / </span>
            <span aria-current="page">How to use</span>
          </nav>

          <p className="eyebrow">Family guide</p>
          <h1 className="section-heading">How to use Krishna Book stories</h1>
          <p className="section-lead how-to-lead">
            A child-drawn weekly path for families, Sunday School, and homeschool — listen, read, create, return to source, then reflect.
          </p>

          <div className="how-to-storyboard" role="list">
            {STEPS.map((step, index) => (
              <article key={step.id} className="how-to-step" role="listitem" id={step.id}>
                <div className="how-to-step-art" aria-hidden="true">
                  <StepDoodle index={index} />
                </div>
                <div className="how-to-step-copy">
                  <p className="how-to-step-num">Step {index + 1}</p>
                  <h2>{step.title}</h2>
                  <p>{step.body}</p>
                  <Link className="bhava-button bhava-button--quiet" href={step.href}>
                    {step.linkLabel}
                  </Link>
                </div>
              </article>
            ))}
          </div>

          <div className="how-to-print-note no-print">
            <p className="hint">
              This page is print-friendly as a one-page family guide. Use your browser&rsquo;s print command when you want a paper copy.
            </p>
            <div className="actions">
              <Link className="bhava-button bhava-button--accent" href="/library/krishna-book">
                Begin with the Krishna Book library
              </Link>
              <Link className="bhava-button bhava-button--quiet" href="/">
                Back to home
              </Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}

function StepDoodle({ index }: { index: number }) {
  const props = {
    width: 160,
    height: 120,
    viewBox: "0 0 160 120",
    fill: "none",
    role: "img" as const,
  };
  switch (index) {
    case 0:
      return (
        <svg {...props} aria-label="Listen doodle">
          <rect x="8" y="8" width="144" height="104" rx="18" fill="#f6ead2" stroke="#c9a66b" strokeWidth="2" strokeDasharray="5 4" />
          <circle cx="58" cy="58" r="28" fill="#12375e" />
          <path d="M48 58l16-10v20l-16-10z" fill="#e8b84a" />
          <path d="M98 40c10 8 10 32 0 40M110 32c16 12 16 44 0 56" stroke="#8a4b12" strokeWidth="3" strokeLinecap="round" />
        </svg>
      );
    case 1:
      return (
        <svg {...props} aria-label="Read doodle">
          <rect x="8" y="8" width="144" height="104" rx="18" fill="#f6ead2" stroke="#c9a66b" strokeWidth="2" strokeDasharray="5 4" />
          <path d="M36 30h88v64H36z" fill="#fffaf0" stroke="#3f6d4f" strokeWidth="2.5" />
          <path d="M48 48h64M48 62h52M48 76h40" stroke="#8a6a3a" strokeWidth="3" strokeLinecap="round" />
        </svg>
      );
    case 2:
      return (
        <svg {...props} aria-label="Create doodle">
          <rect x="8" y="8" width="144" height="104" rx="18" fill="#f6ead2" stroke="#c9a66b" strokeWidth="2" strokeDasharray="5 4" />
          <rect x="40" y="28" width="80" height="64" rx="8" fill="#fff" stroke="#c47a2c" strokeWidth="2.5" />
          <path d="M52 70c10-18 18-8 28-24 8 14 16 8 28 20" stroke="#e8b84a" strokeWidth="4" strokeLinecap="round" />
          <circle cx="118" cy="36" r="8" fill="#f3c9c0" stroke="#a14d3a" strokeWidth="2" />
        </svg>
      );
    case 3:
      return (
        <svg {...props} aria-label="Source doodle">
          <rect x="8" y="8" width="144" height="104" rx="18" fill="#f6ead2" stroke="#c9a66b" strokeWidth="2" strokeDasharray="5 4" />
          <path d="M44 26h72v72H44z" fill="#eef3f8" stroke="#12375e" strokeWidth="2.5" />
          <path d="M56 44h48M56 58h40M56 72h32" stroke="#5a7a9a" strokeWidth="3" strokeLinecap="round" />
          <circle cx="112" cy="84" r="10" fill="#e8b84a" stroke="#8a4b12" strokeWidth="2" />
        </svg>
      );
    default:
      return (
        <svg {...props} aria-label="Reflect doodle">
          <rect x="8" y="8" width="144" height="104" rx="18" fill="#f6ead2" stroke="#c9a66b" strokeWidth="2" strokeDasharray="5 4" />
          <path
            d="M80 86s-22-14-22-30a12 12 0 0 1 22-8 12 12 0 0 1 22 8c0 16-22 30-22 30z"
            fill="#f3c9c0"
            stroke="#a14d3a"
            strokeWidth="2.5"
          />
          <path d="M48 34c8-6 16-4 20 2M112 34c-8-6-16-4-20 2" stroke="#8a4b12" strokeWidth="2.5" strokeLinecap="round" />
        </svg>
      );
  }
}
