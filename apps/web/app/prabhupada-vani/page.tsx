import { PageIntro } from "@/components/page-intro";

export default function PrabhupadaVaniPage() {
  return (
    <>
      <PageIntro
        eyebrow="Prabhupāda Vāṇī"
        title="A space for timeless instruction."
        body="Prepared with care, context, and appropriate source attribution — never as a placeholder dump."
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="coming">
            <div>
              <p className="eyebrow">Coming soon</p>
              <h2>Instruction with reverence</h2>
              <p>
                Prabhupāda Vāṇī will open when curated selections and permissions are ready. Until then, enjoy Krishna
                Book stories in the library.
              </p>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
