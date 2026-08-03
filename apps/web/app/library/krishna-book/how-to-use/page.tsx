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
    href: "/stories/001",
    linkLabel: "Open a story to listen",
  },
  {
    id: "read",
    title: "Read tomorrow",
    body: "Open the Read tab. The words you hear and the words you read come from the same canonical story text.",
    href: "/stories/001",
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
    href: "/stories/001",
    linkLabel: "View an example",
  },
  {
    id: "reflect",
    title: "Reflect and share",
    body: "Write a private note, discuss the lesson together, and optionally share completed work with family or class. No WhatsApp join link is published until an approved URL exists.",
    href: "/library/krishna-book",
    linkLabel: "Browse the story library",
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
        <svg {...props} aria-label="Listen doodle: child in bed with headphones">
          <rect x="8" y="8" width="144" height="104" rx="18" fill="#f6ead2" stroke="#c9a66b" strokeWidth="2" strokeDasharray="5 4" />
          <ellipse cx="80" cy="78" rx="40" ry="14" fill="#ede3d2" />
          <rect x="52" y="52" width="56" height="32" rx="6" fill="#f9f3e8" stroke="#c9a66b" strokeWidth="1.5" />
          <circle cx="80" cy="44" r="14" fill="#fce4c8" stroke="#c47a2c" strokeWidth="1.5" />
          <path d="M68 38c-2-6 4-12 12-12s14 6 12 12" stroke="#8a4b12" strokeWidth="2" strokeLinecap="round" />
          <path d="M66 44h-4a3 3 0 0 0-3 3v4a3 3 0 0 0 3 3h2" stroke="#c47a2c" strokeWidth="2" />
          <path d="M94 44h4a3 3 0 0 1 3 3v4a3 3 0 0 1-3 3h-2" stroke="#c47a2c" strokeWidth="2" />
          <circle cx="76" cy="46" r="1.5" fill="#8a4b12" />
          <circle cx="84" cy="46" r="1.5" fill="#8a4b12" />
          <path d="M76 50c2 2 6 2 8 0" stroke="#a14d3a" strokeWidth="1.2" strokeLinecap="round" />
          <path d="M108 28c4 3 4 12 0 16M116 22c8 6 8 20 0 28" stroke="#e8b84a" strokeWidth="2.5" strokeLinecap="round" opacity="0.7" />
          <circle cx="28" cy="24" r="5" fill="#e8b84a" opacity="0.5" />
          <circle cx="36" cy="16" r="3" fill="#f3c9c0" opacity="0.4" />
          <path d="M24 96l4-6 3 4 5-8 4 6 3-3" stroke="#c9a66b" strokeWidth="1.5" strokeLinecap="round" opacity="0.3" />
        </svg>
      );
    case 1:
      return (
        <svg {...props} aria-label="Read doodle: parent and child with book">
          <rect x="8" y="8" width="144" height="104" rx="18" fill="#f6ead2" stroke="#c9a66b" strokeWidth="2" strokeDasharray="5 4" />
          <rect x="48" y="36" width="64" height="50" rx="6" fill="#fffaf0" stroke="#3f6d4f" strokeWidth="2" />
          <path d="M80 36v50" stroke="#3f6d4f" strokeWidth="1.5" strokeDasharray="3 2" />
          <path d="M56 48h18M56 56h16M56 64h14M56 72h12" stroke="#8a6a3a" strokeWidth="2" strokeLinecap="round" />
          <path d="M86 48h18M86 56h16M86 64h14" stroke="#8a6a3a" strokeWidth="2" strokeLinecap="round" />
          <circle cx="38" cy="52" r="10" fill="#fce4c8" stroke="#c47a2c" strokeWidth="1.5" />
          <circle cx="35" cy="50" r="1.2" fill="#8a4b12" />
          <circle cx="41" cy="50" r="1.2" fill="#8a4b12" />
          <path d="M36 54c1.5 1.5 3 1.5 4 0" stroke="#a14d3a" strokeWidth="1" strokeLinecap="round" />
          <circle cx="122" cy="52" r="8" fill="#fce4c8" stroke="#c47a2c" strokeWidth="1.5" />
          <circle cx="120" cy="50" r="1" fill="#8a4b12" />
          <circle cx="124" cy="50" r="1" fill="#8a4b12" />
          <path d="M120 53c1 1 3 1 4 0" stroke="#a14d3a" strokeWidth="1" strokeLinecap="round" />
          <path d="M18 96l3-5 4 3 5-7 3 5" stroke="#3f6d4f" strokeWidth="1.5" strokeLinecap="round" opacity="0.3" />
        </svg>
      );
    case 2:
      return (
        <svg {...props} aria-label="Create doodle: child coloring with crayons">
          <rect x="8" y="8" width="144" height="104" rx="18" fill="#f6ead2" stroke="#c9a66b" strokeWidth="2" strokeDasharray="5 4" />
          <rect x="36" y="42" width="88" height="56" rx="4" fill="#fff" stroke="#c47a2c" strokeWidth="2" />
          <path d="M48 72c8-14 16-6 24-20 6 12 14 6 24 16" stroke="#e8b84a" strokeWidth="3" strokeLinecap="round" fill="none" />
          <circle cx="108" cy="50" r="6" fill="#f3c9c0" stroke="#a14d3a" strokeWidth="1.5" />
          <rect x="42" y="52" width="6" height="28" rx="2" fill="#e74c3c" transform="rotate(-15 42 52)" />
          <rect x="50" y="54" width="6" height="26" rx="2" fill="#3498db" transform="rotate(-8 50 54)" />
          <rect x="58" y="55" width="6" height="24" rx="2" fill="#2ecc71" transform="rotate(-3 58 55)" />
          <circle cx="80" cy="28" r="10" fill="#fce4c8" stroke="#c47a2c" strokeWidth="1.5" />
          <circle cx="77" cy="26" r="1.2" fill="#8a4b12" />
          <circle cx="83" cy="26" r="1.2" fill="#8a4b12" />
          <path d="M77 30c2 2 4 2 6 0" stroke="#a14d3a" strokeWidth="1" strokeLinecap="round" />
          <path d="M72 18c0-4 6-8 8-6" stroke="#8a4b12" strokeWidth="1.5" strokeLinecap="round" />
          <path d="M88 18c0-4-6-8-8-6" stroke="#8a4b12" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      );
    case 3:
      return (
        <svg {...props} aria-label="Source doodle: scripture book with bookmark">
          <rect x="8" y="8" width="144" height="104" rx="18" fill="#f6ead2" stroke="#c9a66b" strokeWidth="2" strokeDasharray="5 4" />
          <rect x="40" y="22" width="80" height="76" rx="6" fill="#eef3f8" stroke="#12375e" strokeWidth="2.5" />
          <path d="M52 36h56M52 46h48M52 56h40M52 66h44M52 76h36" stroke="#5a7a9a" strokeWidth="2.5" strokeLinecap="round" />
          <rect x="104" y="22" width="12" height="30" rx="2" fill="#e8b84a" stroke="#8a4b12" strokeWidth="1" />
          <path d="M104 52l6 8 6-8" fill="#e8b84a" stroke="#8a4b12" strokeWidth="1" />
          <circle cx="28" cy="60" r="12" fill="none" stroke="#12375e" strokeWidth="2" />
          <path d="M36 68l6 6" stroke="#12375e" strokeWidth="2.5" strokeLinecap="round" />
          <path d="M130 80l-4-6 4-2 4 2-4 6z" fill="#e8b84a" opacity="0.5" />
        </svg>
      );
    default:
      return (
        <svg {...props} aria-label="Reflect doodle: family sharing together">
          <rect x="8" y="8" width="144" height="104" rx="18" fill="#f6ead2" stroke="#c9a66b" strokeWidth="2" strokeDasharray="5 4" />
          <path
            d="M80 82s-20-12-20-28a11 11 0 0 1 20-6 11 11 0 0 1 20 6c0 16-20 28-20 28z"
            fill="#f3c9c0"
            stroke="#a14d3a"
            strokeWidth="2"
          />
          <circle cx="46" cy="50" r="10" fill="#fce4c8" stroke="#c47a2c" strokeWidth="1.5" />
          <circle cx="43" cy="48" r="1.2" fill="#8a4b12" />
          <circle cx="49" cy="48" r="1.2" fill="#8a4b12" />
          <path d="M44 52c1.5 1.5 3 1.5 4 0" stroke="#a14d3a" strokeWidth="1" strokeLinecap="round" />
          <circle cx="114" cy="50" r="10" fill="#fce4c8" stroke="#c47a2c" strokeWidth="1.5" />
          <circle cx="111" cy="48" r="1.2" fill="#8a4b12" />
          <circle cx="117" cy="48" r="1.2" fill="#8a4b12" />
          <path d="M112 52c1.5 1.5 3 1.5 4 0" stroke="#a14d3a" strokeWidth="1" strokeLinecap="round" />
          <circle cx="80" cy="36" r="8" fill="#fce4c8" stroke="#c47a2c" strokeWidth="1.5" />
          <circle cx="78" cy="34" r="1" fill="#8a4b12" />
          <circle cx="82" cy="34" r="1" fill="#8a4b12" />
          <path d="M78 37c1 1 3 1 4 0" stroke="#a14d3a" strokeWidth="1" strokeLinecap="round" />
          <path d="M50 34c6-4 12-3 16 2M110 34c-6-4-12-3-16 2" stroke="#8a4b12" strokeWidth="2" strokeLinecap="round" />
        </svg>
      );
  }
}
