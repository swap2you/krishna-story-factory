import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import { brandSrc } from "@/lib/brand-assets";

export const metadata: Metadata = {
  title: "Learning",
  description:
    "Honest learning pathways for children, families, Sunday School, teachers, preachers, Gurukula/homeschool, and festival use — linking only to real Bhāva pages.",
};

type Pathway = {
  title: string;
  href: string;
  status: "available" | "planned";
  audience: string;
  body: string;
};

const PATHWAYS: Pathway[] = [
  {
    title: "Children & Youth",
    href: "/learning/children-youth",
    status: "available",
    audience: "Ages 5–20",
    body: "Age-band routes into stories, Knowledge, and printables — without treating teenagers like little children.",
  },
  {
    title: "Families",
    href: "/learning/families",
    status: "available",
    audience: "Homes and caregivers",
    body: "Calm home practice routes into Printables and public Knowledge guides. No fake take-home downloads.",
  },
  {
    title: "Sunday School",
    href: "/sunday-school",
    status: "available",
    audience: "Weekly classes",
    body: "Usable weekly planner, homework checklist, and parent message template. Festival unit packs remain Planned on that page.",
  },
  {
    title: "Teachers",
    href: "/teachers",
    status: "available",
    audience: "Classroom facilitators",
    body: "Classroom playlist helper and lesson packing tools grounded in released Krishna Book stories.",
  },
  {
    title: "Preachers",
    href: "/preachers",
    status: "available",
    audience: "Outreach and programs",
    body: "Select released stories, preview source references, and export outlines for programs.",
  },
  {
    title: "Gurukula / Homeschool",
    href: "/learning/gurukula-homeschool",
    status: "planned",
    audience: "Home and Gurukula educators",
    body: "Dedicated curriculum packs are still forming. This pathway links only to real Teachers, Knowledge, and Printables pages today.",
  },
  {
    title: "Festival use",
    href: "/learning/festivals",
    status: "planned",
    audience: "Seasonal programs",
    body: "Festival unit shells are named honestly. Multi-week packs are Planned; use Sunday School and Stories for what exists now.",
  },
];

export default function LearningHubPage() {
  return (
    <>
      <PageIntro
        eyebrow="Learning"
        title="Pathways for growing devotees."
        body="Learning serves children, families, teachers, preachers, and communities. Each pathway links only to a real page, with Available or Planned labeled honestly."
        heroSrc={brandSrc("collection-sunday-school")}
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="scope-grid" style={{ marginBottom: "2rem" }}>
            <article className="scope-card">
              <h3>Available now</h3>
              <p>
                Children &amp; Youth, Families, Sunday School planner, Teachers classroom helper, and Preachers
                workspace — grounded in released Krishna Book stories and public Knowledge pages.
              </p>
            </article>
            <article className="scope-card">
              <h3>Still planned</h3>
              <p>
                Dedicated Gurukula/homeschool curriculum packs and festival unit packs remain Planned. They are
                labeled clearly so nothing looks published before it is ready — and never as fake downloads.
              </p>
            </article>
          </div>

          <h2 className="section-heading">Learning pathways</h2>
          <p className="section-lead">
            Choose a pathway. Planned destinations stay open as honest shells — never as fake downloads.
          </p>
          <div className="scope-grid">
            {PATHWAYS.map((pathway) => (
              <article key={pathway.href} className="scope-card">
                <h3 style={{ marginTop: 0 }}>
                  <Link href={pathway.href}>{pathway.title}</Link>
                </h3>
                <p className="hint" style={{ marginBottom: ".65rem" }}>
                  {pathway.audience}
                </p>
                <p style={{ marginBottom: ".85rem" }}>{pathway.body}</p>
                <span
                  className={`editorial-status ${pathway.status === "available" ? "active" : "planned"}`}
                >
                  {pathway.status === "available" ? "Available" : "Planned"}
                </span>
              </article>
            ))}
          </div>

          <p className="hint" style={{ marginTop: "2rem" }}>
            Looking for story printables? Visit the{" "}
            <Link href="/printables">Printables hub</Link>. For source-led study, start in{" "}
            <Link href="/knowledge">Knowledge</Link>.
          </p>
        </div>
      </section>
    </>
  );
}
