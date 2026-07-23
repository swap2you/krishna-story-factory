import { PageIntro } from "@/components/page-intro";

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
          <div className="coming">
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
