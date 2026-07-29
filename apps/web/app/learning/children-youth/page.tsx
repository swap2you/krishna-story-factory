import Link from "next/link";

const bands = [
  {
    title: "Little Listeners",
    ages: "5–7",
    body: "Short listens, gentle stories, and simple coloring pages that stay warm and clear.",
  },
  {
    title: "Young Explorers",
    ages: "8–12",
    body: "Fuller Krishna Book chapters, printable activities, and family discussion prompts.",
  },
  {
    title: "Teen Seekers",
    ages: "13–15",
    body: "Honest questions, Knowledge pathways, and age-respectful language — never childish framing.",
  },
  {
    title: "Youth Leaders",
    ages: "16–20",
    body: "Teacher and preacher-ready structures, leadership practice, and source-reviewed outlines.",
  },
];

export default function ChildrenYouthPage() {
  return (
    <div className="container section">
      <p className="eyebrow">Learning</p>
      <h1 className="section-heading">Children & Youth</h1>
      <p className="section-lead">
        Age-band routes into stories, Knowledge, prayers, printables, and pathways — without treating teenagers like
        little children.
      </p>
      <div className="audience-grid">
        {bands.map((band) => (
          <article key={band.title} className="audience-card">
            <h2>{band.title}</h2>
            <p className="hint">Ages {band.ages}</p>
            <p>{band.body}</p>
            <div className="actions">
              <Link className="bhava-button bhava-button--quiet" href="/library/krishna-book">Stories</Link>
              <Link className="bhava-button bhava-button--quiet" href="/knowledge">Knowledge</Link>
              <Link className="bhava-button bhava-button--quiet" href="/printables">Printables</Link>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
