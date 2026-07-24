import type { Metadata } from "next";
import { PageIntro } from "@/components/page-intro";

export const metadata: Metadata = {
  title: "Editorial standards",
  description: "How Bhāva Knowledge Library reviews sources, rights, and confidential content.",
};

export default function KnowledgeStandardsPage() {
  return (
    <>
      <PageIntro
        eyebrow="Knowledge"
        title="Editorial standards"
        body="Publication requires source tiers, rights clarity, and confidential-content gates. Restricted initiation or mantra material is never published."
      />
      <section className="section">
        <div className="container prose" style={{ maxWidth: 760 }}>
          <h2>Source authority tiers</h2>
          <ul>
            <li><strong>A1</strong> — Governing primary sources (Prabhupāda; GBC/ministry within mandate)</li>
            <li><strong>A2</strong> — Approved Gauḍīya educational and research sources</li>
            <li><strong>B1/B2</strong> — Comparative or manuscript sources with labels</li>
            <li><strong>C1</strong> — Academic secondary context (never sole practice basis)</li>
            <li><strong>D</strong> — Discovery only; cannot establish a published conclusion</li>
          </ul>
          <h2>Quotation types</h2>
          <p>Direct quote, translation, paraphrase, adaptation, explanation, and reflection are labeled distinctly.</p>
          <h2>Publication gates</h2>
          <ul>
            <li>Unknown rights → blocked</li>
            <li>Unreviewed sacred text → blocked</li>
            <li>Confidential initiation/mantra content → blocked and absent from public bundles</li>
            <li>Fabricated citation → blocked</li>
            <li>Missing required reviewer → blocked</li>
          </ul>
          <h2>Public identity</h2>
          <p>Svarna Gauranga Das · svarnagaurangdas@gmail.com · Harrisburg, Pennsylvania</p>
        </div>
      </section>
    </>
  );
}
