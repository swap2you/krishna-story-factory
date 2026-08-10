import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";

export const metadata: Metadata = {
  title: "Families — Learning",
  description:
    "Home practice routes for families into real Bhāva Printables and Knowledge guides — no fake downloads.",
};

const LINKS = [
  {
    title: "Printables hub",
    href: "/printables",
    body: "Released posters, coloring pages, and activity sheets for Stories 001–025.",
    status: "available" as const,
  },
  {
    title: "Printing and classroom use",
    href: "/knowledge/printing-and-classroom-use",
    body: "How families and teachers can print from released packages without mistaking Bhāva for official BBT publications.",
    status: "available" as const,
  },
  {
    title: "What is Bhāva?",
    href: "/knowledge/what-is-bhava",
    body: "A short, source-honest introduction you can read together at home.",
    status: "available" as const,
  },
  {
    title: "Krishna Book stories",
    href: "/library/krishna-book",
    body: "Bedtime and family listening from the active story library.",
    status: "available" as const,
  },
  {
    title: "Family practice packs",
    href: "/learning",
    body: "Structured take-home derivative packs are still in draft under content/learning — not advertised as public downloads yet.",
    status: "planned" as const,
  },
];

export default function FamiliesLearningPage() {
  return (
    <>
      <PageIntro
        eyebrow="Learning · Families"
        title="Calm practice at home."
        body="This pathway points only to real pages and released assets. Planned family packs stay labeled Planned — never as fake downloads."
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
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
