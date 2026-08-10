import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";

export const metadata: Metadata = {
  title: "Gurukula / Homeschool — Learning",
  description:
    "Planned Gurukula and homeschool pathway with honest links to real Teachers, Knowledge, and Printables pages.",
};

const LINKS = [
  {
    title: "For Teachers",
    href: "/teachers",
    body: "Classroom playlist helper you can adapt for home or Gurukula sessions.",
    status: "available" as const,
  },
  {
    title: "Knowledge",
    href: "/knowledge",
    body: "Source-led guides and pathways — use only approved public records.",
    status: "available" as const,
  },
  {
    title: "Printables",
    href: "/printables",
    body: "Released story print assets for hands-on practice.",
    status: "available" as const,
  },
  {
    title: "Children & Youth age bands",
    href: "/learning/children-youth",
    body: "Age-respectful routes so teens are not framed as little children.",
    status: "available" as const,
  },
  {
    title: "Gurukula / homeschool curriculum packs",
    href: "/learning/gurukula-homeschool",
    body: "Dedicated multi-week packs, pacing charts, and assessment sets are Planned. Nothing is offered as a fake download here.",
    status: "planned" as const,
  },
];

export default function GurukulaHomeschoolPage() {
  return (
    <>
      <PageIntro
        eyebrow="Learning · Gurukula / Homeschool"
        title="Home and Gurukula learning — building carefully."
        body="Dedicated curriculum packs are Planned. Until they ship, use the real Teachers, Knowledge, and Printables surfaces linked below."
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <p className="section-lead" style={{ marginTop: 0 }}>
            <span className="editorial-status planned">Planned pathway</span>
          </p>
          <div className="scope-grid">
            {LINKS.map((item) => (
              <article key={item.title} className="scope-card">
                <h3 style={{ marginTop: 0 }}>
                  {item.status === "available" ? (
                    <Link href={item.href}>{item.title}</Link>
                  ) : (
                    item.title
                  )}
                </h3>
                <p style={{ marginBottom: ".85rem" }}>{item.body}</p>
                <span
                  className={`editorial-status ${item.status === "available" ? "active" : "planned"}`}
                >
                  {item.status === "available" ? "Available" : "Planned"}
                </span>
              </article>
            ))}
          </div>
          <p className="hint" style={{ marginTop: "2rem" }}>
            Back to the <Link href="/learning">Learning hub</Link>.
          </p>
        </div>
      </section>
    </>
  );
}
