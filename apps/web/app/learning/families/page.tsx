import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import {
  audienceLabel,
  listPublicDerivativeMetas,
} from "@/lib/learning/derivatives";

export const metadata: Metadata = {
  title: "Families — Learning",
  description:
    "Home practice routes for families into real Bhāva Printables, Knowledge guides, and published Learning derivatives — no fake downloads.",
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
];

export default function FamiliesLearningPage() {
  const familyDerivatives = listPublicDerivativeMetas().filter((d) =>
    d.audience.profiles.includes("families"),
  );

  return (
    <>
      <PageIntro
        eyebrow="Learning · Families"
        title="Calm practice at home."
        body="This pathway points only to real pages, released assets, and published Bhāva-original derivatives. Nothing is advertised as a download unless a validated export exists."
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <h2 className="section-heading">Published family derivatives</h2>
          {familyDerivatives.length ? (
            <div className="scope-grid" style={{ marginBottom: "2rem" }}>
              {familyDerivatives.map((d) => (
                <article key={d.slug} className="scope-card">
                  <h3 style={{ marginTop: 0 }}>
                    <Link href={`/learning/derivatives/${d.slug}`}>{d.title}</Link>
                  </h3>
                  <p className="hint" style={{ marginBottom: ".5rem" }}>
                    {audienceLabel(d)}
                  </p>
                  <p style={{ marginBottom: ".65rem" }}>{d.learning_objective}</p>
                  <p className="hint" style={{ marginBottom: ".65rem" }}>
                    Lineage: {d.canonical_record_version.record_slug} ·{" "}
                    {d.review_state} · in-page only
                  </p>
                  <span className="editorial-status active">Available</span>
                </article>
              ))}
            </div>
          ) : (
            <p className="hint" style={{ marginBottom: "2rem" }}>
              Family derivatives will appear here when published.
            </p>
          )}

          <h2 className="section-heading">Related pages</h2>
          <div className="scope-grid">
            {LINKS.map((item) => (
              <article key={item.title} className="scope-card">
                <h3 style={{ marginTop: 0 }}>
                  <Link href={item.href}>{item.title}</Link>
                </h3>
                <p style={{ marginBottom: ".85rem" }}>{item.body}</p>
                <span className="editorial-status active">Available</span>
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
