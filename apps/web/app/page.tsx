import Link from "next/link";
import { getStories } from "@/lib/catalog";
import { StoryGrid } from "@/components/story-grid";

export const dynamic = "force-dynamic";

export default async function Home() {
  const stories = await getStories();
  const latest = stories.slice(-3).reverse();
  const featured = stories.find((story) => story.poster_url) ?? stories[0];

  return (
    <>
      <section className="hero">
        <div className="hero-grid">
          <div className="hero-copy">
            <p className="hero-badge">❀ Radha-Krishna · Family library</p>
            <p className="brand-kicker">Bhāva</p>
            <h1>Stories that bring little hearts closer to Krishna.</h1>
            <p className="hero-copy-text">
              A calm, luxurious home for Krishna Book bedtime stories — listen, read, color, and learn together.
            </p>
            <div className="actions">
              <Link className="bhava-button bhava-button--accent" href="/library/krishna-book">
                Open Krishna Book
              </Link>
              <Link className="bhava-button bhava-button--quiet" href="/teachers">
                For teachers
              </Link>
            </div>
            <div className="hero-meta">
              <div><strong>{stories.length || "7"}</strong><span>Stories ready</span></div>
              <div><strong>Audio + PDF</strong><span>Listen & activities</span></div>
              <div><strong>Local notes</strong><span>Private on this device</span></div>
            </div>
          </div>
          <div className="hero-art">
            {featured?.poster_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={featured.poster_url}
                alt={`${featured.title} story poster`}
              />
            ) : (
              <div style={{ height: "100%", minHeight: 320, background: "linear-gradient(145deg,#12325a,#6a3a4a)" }} aria-hidden="true" />
            )}
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <p className="eyebrow">Scripture shelves</p>
          <h2 className="section-heading">A growing divine library</h2>
          <p className="section-lead">Begin with Krishna Book. Future collections wait as polished coming-soon shelves — never empty dead ends.</p>
          <div className="collection-grid">
            <Link href="/library/krishna-book" className="collection-card krishna">
              <h3>Krishna Book</h3>
              <p>Bedtime stories 001–007 with audio, coloring, and activities.</p>
              <span className="orb" aria-hidden="true" />
            </Link>
            <div className="collection-card lotus">
              <h3>Śrīmad-Bhāgavatam</h3>
              <p>Cantos 1–12 — structure ready, content coming with care.</p>
              <span className="orb" aria-hidden="true" />
            </div>
            <div className="collection-card forest">
              <h3>Rāmāyaṇa & more</h3>
              <p>Future shelves for Caitanya literature and Vāṇī resources.</p>
              <span className="orb" aria-hidden="true" />
            </div>
          </div>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <p className="eyebrow">Continue listening</p>
          <h2 className="section-heading">Latest released stories</h2>
          <StoryGrid stories={latest.length ? latest : stories} empty="Start the local API to discover Stories 001–007." />
        </div>
      </section>
    </>
  );
}
