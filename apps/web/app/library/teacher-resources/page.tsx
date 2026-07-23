import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";

export const metadata: Metadata = {
  title: "Teacher Resources",
  description: "Curriculum guides, classroom materials, and structured plans for devotional education.",
};

const PLANNED_RESOURCES = [
  { title: "Curriculum guides", desc: "Structured semester and year-long plans mapping scripture collections to age groups and learning objectives." },
  { title: "Lesson plan templates", desc: "Printable templates combining story, audio, coloring, and activity assets into ready-to-use classroom sessions." },
  { title: "Assessment rubrics", desc: "Gentle, non-competitive rubrics for tracking engagement and comprehension without pressure." },
  { title: "Festival unit plans", desc: "Multi-week units centered around Janmāṣṭamī, Gaura Pūrṇimā, Rāma Navamī, and other celebrations." },
  { title: "Parent communication", desc: "Templates for weekly updates, homework summaries, and take-home activity instructions." },
  { title: "Classroom setup guides", desc: "Practical advice for arranging a devotional classroom, managing mixed-age groups, and creating a calm learning environment." },
];

export default function TeacherResourcesPage() {
  return (
    <>
      <PageIntro
        eyebrow="Scripture collection"
        title="Teacher Resources"
        body="Curriculum guides, classroom materials, and structured plans — built to support devotional educators at every level."
      />
      <section className="section">
        <div className="container">
          <div className="scope-grid" style={{ marginBottom: "2rem" }}>
            <article className="scope-card">
              <h3>Purpose</h3>
              <p>Equip Sunday school teachers, home-schooling parents, and preaching educators with structured materials that pair directly with Bhāva story collections.</p>
            </article>
            <article className="scope-card">
              <h3>Audience</h3>
              <p>ISKCON Sunday school teachers, home-school families, gurukula educators, and community preaching teams.</p>
            </article>
          </div>

          <h2 className="section-heading">Planned resources</h2>
          <div className="scope-grid">
            {PLANNED_RESOURCES.map((r) => (
              <article key={r.title} className="scope-card">
                <h3>{r.title}</h3>
                <p>{r.desc}</p>
              </article>
            ))}
          </div>

          <div className="coming" style={{ marginTop: "2rem" }}>
            <div>
              <p className="eyebrow">Coming soon</p>
              <h2>Teacher materials in development</h2>
              <p>
                Resources will be designed in collaboration with experienced devotional educators.
                In the meantime, visit the <Link href="/teachers" style={{ color: "var(--bhava-saffron)", fontWeight: 700 }}>For Teachers</Link> page
                to build class packs from existing Krishna Book stories.
              </p>
              <p className="hint" style={{ marginTop: "1rem" }}>
                <span className="editorial-status planned">Planned</span>
              </p>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
