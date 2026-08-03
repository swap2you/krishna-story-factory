import Link from "next/link";
import { getBhavaReleaseMeta } from "@/lib/release-meta";

const trustLinks = [
  ["About", "/about"],
  ["Contact", "/contact"],
  ["Copyright", "/rights"],
  ["Privacy", "/privacy"],
  ["Accessibility", "/accessibility"],
] as const;

export function SiteFooter() {
  const meta = getBhavaReleaseMeta();
  const env =
    process.env.BHAVA_ENVIRONMENT?.trim() ||
    process.env.NEXT_PUBLIC_BHAVA_ENV?.trim() ||
    process.env.NODE_ENV ||
    "development";

  return (
    <footer className="site-footer site-footer--bar">
      <div className="container footer-bar">
        <div className="footer-bar__brand">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            className="brand-logo-footer brand-logo-footer--compact"
            src="/brand/logo-dark-bg.webp"
            alt=""
            width={96}
            height={36}
            aria-hidden="true"
          />
          <p className="footer-copyright footer-copyright--bar">
            © 2026 Svarna Gauranga Das (Swapnil Patil) · Dauji Publication · Bhāva
          </p>
        </div>
        <nav className="footer-bar__links" aria-label="Trust and contact">
          {trustLinks.map(([label, href]) => (
            <Link key={href} href={href}>
              {label}
            </Link>
          ))}
          <details className="footer-version-details footer-version-details--bar">
            <summary className="footer-version-toggle">Version</summary>
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
        </nav>
      </div>
    </footer>
  );
}
