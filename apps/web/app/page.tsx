import Link from "next/link";
import { getStories } from "@/lib/catalog";
import { StoryGrid } from "@/components/story-grid";

export default async function Home() {
  const stories = await getStories();
  const latest = stories.slice(-3).reverse();

  return (
    <>
      <section className="hero">
        <div className="container hero-content">
          <p className="brand-kicker">Bhāva</p>
          <h1>Stories that bring little hearts closer to Krishna.</h1>
          <p className="hero-copy">
            A calm home for Krishna Book bedtime stories — listen, read, color, and learn together.
          </p>
          <div className="actions">
            <Link className="bhava-button bhava-button--accent" href="/library/krishna-book">
              Open Krishna Book
            </Link>
            <Link className="bhava-button bhava-button--quiet" href="/teachers">
              For teachers
            </Link>
          </div>
        </div>
      </section>
      <section className="section">
        <div className="container">
          <p className="eyebrow">Continue listening</p>
          <h2 className="section-heading">Latest released stories</h2>
          <StoryGrid stories={latest.length ? latest : stories} empty="Start the local API to discover Stories 001–007." />
        </div>
      </section>
    </>
  );
}
