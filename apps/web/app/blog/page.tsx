import type { Metadata } from "next";
import { PageIntro } from "@/components/page-intro";

export const metadata: Metadata = {
  title: "Bhakti Blog",
  description: "Practical, warm reflections for families and learners — arriving when they are ready.",
};

const TAXONOMY = [
  { label: "Family practice", desc: "Tips for weaving devotion into daily family routines." },
  { label: "Teaching notes", desc: "Insights and strategies for devotional educators." },
  { label: "Festival reflections", desc: "Seasonal essays tied to the Vaiṣṇava calendar." },
  { label: "Behind the stories", desc: "How Bhāva stories are researched, written, and reviewed." },
  { label: "Śloka study", desc: "Accessible explorations of key verses and their meaning." },
];

const PLANNED_ARTICLES = [
  {
    title: "How we choose a bedtime story from the Krishna Book",
    desc: "A look at the editorial process — from chapter selection to source verification, narration recording, and senior review — that shapes every Bhāva story package.",
    audience: "Parents and teachers",
    tags: ["Behind the stories"],
  },
  {
    title: "Building a morning sādhana routine with young children",
    desc: "Practical ideas for families who want to introduce maṅgala-ārati prayers, simple japa, and short readings without overwhelming small children.",
    audience: "Parents of ages 3–8",
    tags: ["Family practice"],
  },
  {
    title: "Preparing a Janmāṣṭamī class for mixed-age Sunday school",
    desc: "How to structure a multi-week festival unit that keeps Bal Gopal and Dāmodara groups engaged with age-appropriate activities and shared celebrations.",
    audience: "Sunday school teachers",
    tags: ["Teaching notes", "Festival reflections"],
  },
  {
    title: "What makes a faithful retelling? Source governance in children's scripture",
    desc: "Exploring the principles that guide faithful adaptation — how to honor the original text while making it accessible, and why we never fabricate quotations.",
    audience: "Educators and parents",
    tags: ["Behind the stories"],
  },
  {
    title: "Five verses every young devotee can learn this year",
    desc: "A gentle roadmap for introducing children to key Bhagavad-gītā and Bhāgavatam verses — with pronunciation tips, meaning summaries, and memorization games.",
    audience: "Families and teachers",
    tags: ["Śloka study", "Family practice"],
  },
];

export default function BlogPage() {
  return (
    <>
      <PageIntro
        eyebrow="Bhakti Blog"
        title="Notes for a devotional life."
        body="Practical, warm reflections for families and learners — arriving when they are ready."
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <h2 className="section-heading">Topics</h2>
          <p className="section-lead">Articles will be organized by these categories. More may be added as the blog grows.</p>
          <div className="category-grid" style={{ marginBottom: "3rem" }}>
            {TAXONOMY.map((t) => (
              <article key={t.label} className="category-card">
                <h3>{t.label}</h3>
                <p>{t.desc}</p>
              </article>
            ))}
          </div>

          <h2 className="section-heading">Planned articles</h2>
          <p className="section-lead">
            These five articles are in preparation. No article bodies or fabricated quotations exist yet —
            each will be written, reviewed, and published when ready.
          </p>
          <div style={{ display: "grid", gap: "1rem" }}>
            {PLANNED_ARTICLES.map((article) => (
              <article key={article.title} className="blog-card">
                <h3>{article.title}</h3>
                <p style={{ margin: ".35rem 0 0", color: "var(--bhava-muted)", lineHeight: 1.6 }}>{article.desc}</p>
                <div className="blog-meta">
                  {article.tags.map((tag) => (
                    <span key={tag} className="blog-tag">{tag}</span>
                  ))}
                  <span className="blog-audience">{article.audience}</span>
                  <span className="editorial-status planned">Planned</span>
                </div>
              </article>
            ))}
          </div>

          <div className="coming" style={{ marginTop: "2.5rem" }}>
            <div>
              <p className="eyebrow">Coming soon</p>
              <h2>Quiet essays, not noise</h2>
              <p>
                Bhakti Blog will share short reflections for parents and teachers — never rushed, never invented from
                empty sources. Stewarded by Svarna Gauranga Das.
              </p>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
