import Link from "next/link";
import { PageIntro } from "@/components/page-intro";

export default function TeachersPage() {
  return (
    <>
      <PageIntro
        eyebrow="Learning · For Teachers"
        title="Classroom pathways ready for reviewed class packs."
        body="Class structures, source notes, age adaptation, printables, and playlists — published only when reviewed. Direct route /teachers stays available from Learning and the footer."
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container audience-grid">
          <article className="audience-card">
            <h2>Class packs</h2>
            <p>Lesson shells and answer keys will publish here after editorial review.</p>
          </article>
          <article className="audience-card">
            <h2>Printables</h2>
            <p>Use package-backed posters and activity sheets from published stories.</p>
            <Link className="bhava-button bhava-button--quiet" href="/printables">Open Printables</Link>
          </article>
          <article className="audience-card">
            <h2>Children & Youth</h2>
            <p>Age-band routes for 5–20 without infantilizing teens or youth leaders.</p>
            <Link className="bhava-button bhava-button--quiet" href="/learning/children-youth">Open pathway</Link>
          </article>
        </div>
      </section>
    </>
  );
}
