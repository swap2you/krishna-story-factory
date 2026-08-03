import Link from "next/link";
import { getBhavaReleaseMeta } from "@/lib/release-meta";

const groups = [
  {
    title: "Explore",
    links: [
      ["Home", "/"],
      ["Library", "/library"],
      ["Krishna Book", "/library/krishna-book"],
      ["Knowledge", "/knowledge"],
      ["Printables", "/printables"],
    ],
  },
  {
    title: "Learning",
    links: [
      ["Children & Youth", "/learning/children-youth"],
      ["Sunday School", "/sunday-school"],
      ["For Teachers", "/teachers"],
      ["For Preachers", "/preachers"],
    ],
  },
  {
    title: "Trust & Contact",
    links: [
      ["About", "/about"],
      ["Contact", "/contact"],
      ["Copyright & Permissions", "/rights"],
      ["Privacy", "/privacy"],
      ["Accessibility", "/accessibility"],
    ],
  },
] as const;

export function SiteFooter() {
  const meta = getBhavaReleaseMeta();
  const env =
    process.env.BHAVA_ENVIRONMENT?.trim() ||
    process.env.NEXT_PUBLIC_BHAVA_ENV?.trim() ||
    process.env.NODE_ENV ||
    "development";

  return (
    <footer className="site-footer">
      <div className="container footer-grid footer-grid--compact">
        <div className="footer-brand">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            className="brand-logo-footer"
            src="/brand/logo-dark-bg.webp"
            alt="Bhāva"
            width={160}
            height={61}
          />
          <p className="brand-display footer-wordmark">Bhāva</p>
          <p>
            Timeless devotion for growing hearts and minds.
          </p>
          <p className="hint footer-copyright">
            © 2026 Svarna Gauranga Das (Swapnil Patil) · Dauji Publication · Bhāva
          </p>
          <details className="footer-version-details">
            <summary className="hint footer-version-toggle">Version</summary>
            <dl className="footer-version-dl hint">
              <div>
                <dt>Env</dt>
                <dd>{env}</dd>
              </div>
              <div>
                <dt>Web</dt>
                <dd>{meta.webVersion}</dd>
              </div>
              <div>
                <dt>Content</dt>
                <dd>{meta.contentRelease}</dd>
              </div>
              <div>
                <dt>Build</dt>
                <dd>{meta.shortSha}</dd>
              </div>
            </dl>
          </details>
        </div>
        {groups.map((group) => (
          <div key={group.title} className="footer-group">
            <h2>{group.title}</h2>
            <div className="footer-links">
              {group.links.map(([label, href]) => (
                <Link key={href} href={href}>{label}</Link>
              ))}
            </div>
          </div>
        ))}
      </div>
    </footer>
  );
}
