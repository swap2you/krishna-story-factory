import Link from "next/link";

const groups = [
  {
    title: "Explore",
    links: [
      ["Home", "/"],
      ["Library", "/library"],
      ["Knowledge", "/knowledge"],
      ["Prabhupāda Vāṇī", "/prabhupada-vani"],
    ],
  },
  {
    title: "Learning",
    links: [
      ["Children & Youth", "/learning/children-youth"],
      ["Sunday School", "/sunday-school"],
      ["For Teachers", "/teachers"],
      ["For Preachers", "/preachers"],
      ["Printables", "/printables"],
    ],
  },
  {
    title: "About & Contact",
    links: [
      ["About", "/about"],
      ["Contact", "/contact"],
      ["FAQ", "/faq"],
    ],
  },
  {
    title: "Trust & Policies",
    links: [
      ["Copyright & Permissions", "/rights"],
      ["Sources & Permissions", "/source-permissions"],
      ["Editorial Standards", "/knowledge/standards"],
      ["Privacy", "/privacy"],
      ["Accessibility", "/accessibility"],
    ],
  },
] as const;

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="container footer-grid">
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
            Timeless devotion for growing hearts and minds. Stories, scripture, practice, and learning paths for
            children, youth, families, and teachers.
          </p>
          <p className="hint">Stewarded with care by Svarna Gauranga Das · Harrisburg, Pennsylvania</p>
          <p className="hint footer-copyright">
            © 2026 Svarna Gauranga Das. All rights reserved.
            <br />
            Published by Dauji Publication · A Bhāva Project publication
          </p>
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
