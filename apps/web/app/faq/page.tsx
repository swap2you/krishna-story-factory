import Link from "next/link";
import contact from "@/config/contact.json";
import { PageIntro } from "@/components/page-intro";

const FAQS: { q: string; a: string }[] = [
  {
    q: "What is Bhāva?",
    a: "Bhāva is an independent devotional-learning portal that presents child-friendly Krishna Book bedtime stories with listening, reading, coloring, and teaching tools.",
  },
  {
    q: "Who is it for?",
    a: "Children, parents, teachers, Sunday Schools, and preachers who want calm, source-aware Krishna Book learning materials.",
  },
  {
    q: "What ages?",
    a: "Released stories target roughly ages 5–13, with simpler and deeper activity options. Adult caregivers guide younger listeners.",
  },
  {
    q: "What are the sources?",
    a: "Story packages cite Krishna Book and related Śrīmad-Bhāgavatam boundaries. Open Vedabase links support study. Bhāva does not republish full BBT books.",
  },
  {
    q: "Is AI used?",
    a: "AI may assist drafting and production tooling. Human review and source fidelity remain required before public release.",
  },
  {
    q: "How is content reviewed?",
    a: "Released packages must pass quality gates. Public reader text excludes internal production notes. Ślokas and long quotations stay pending until reviewed.",
  },
  {
    q: "Can resources be printed?",
    a: "Yes. Activity PDFs, coloring pages, and posters can be downloaded or opened to print from story pages and the Printables hub.",
  },
  {
    q: "Can teachers use them?",
    a: "Yes. Teachers, Sunday School, and Preachers workspaces provide class-pack and outline tools grounded in released package facts.",
  },
  {
    q: "Why are sections planned?",
    a: "Library collections beyond the current Krishna Book sequence are marked planned until curated, source-reviewed content is ready. We do not invent titles or dates.",
  },
  {
    q: "How to submit corrections?",
    a: `Use Contact with topic “Content correction,” or email ${contact.public_email}.`,
  },
  {
    q: "Are notes private?",
    a: "Family notes stay in the browser (localStorage) on your device. Bhāva does not upload child notes.",
  },
  {
    q: "Is Bhāva an official BBT publication?",
    a: "No. Bhāva is independent stewardship. It does not claim to be the Bhaktivedanta Book Trust or to hold blanket republication rights.",
  },
  {
    q: "Can content be reused?",
    a: "Treat package assets as classroom/family learning aids under the project’s source-and-permissions guidance. Do not redistribute unlicensed full books.",
  },
  {
    q: "Does the site collect child data?",
    a: "No child accounts or submissions. Notes remain local. Contact forms open your own email app and are not stored by Bhāva.",
  },
  {
    q: "How to contact the project?",
    a: `${contact.steward_name}, ${contact.location_city}, ${contact.location_state}. Email ${contact.public_email} or use the Contact form.`,
  },
];

export default function FaqPage() {
  return (
    <>
      <PageIntro
        eyebrow="FAQ"
        title="Clear answers for families and teachers."
        body="Honest guidance about sources, privacy, printing, and how Bhāva is stewarded."
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container" style={{ maxWidth: 760 }}>
          {FAQS.map((item) => (
            <article key={item.q} className="contact-card" style={{ marginBottom: "1rem" }}>
              <h2 style={{ fontSize: "1.15rem", marginTop: 0 }}>{item.q}</h2>
              <p className="hint" style={{ marginBottom: 0 }}>{item.a}</p>
            </article>
          ))}
          <p className="hint">
            More detail: <Link href="/source-permissions">Source & permissions</Link>
            {" · "}
            <Link href="/privacy">Privacy</Link>
            {" · "}
            <Link href="/contact">Contact</Link>
          </p>
        </div>
      </section>
    </>
  );
}
