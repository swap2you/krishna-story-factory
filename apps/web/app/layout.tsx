import type { Metadata } from "next";
import { Fraunces, Source_Sans_3 } from "next/font/google";
import Link from "next/link";
import "@bhava/ui/styles.css";
import "./globals.css";

const display = Fraunces({ subsets: ["latin"], variable: "--font-display" });
const body = Source_Sans_3({ subsets: ["latin"], variable: "--font-body" });

export const metadata: Metadata = {
  title: { default: "Bhāva — Stories for the heart", template: "%s | Bhāva" },
  description: "A premium devotional learning home for Krishna Book stories, families, and teachers.",
  manifest: "/manifest.webmanifest",
  openGraph: {
    title: "Bhāva",
    description: "Devotional learning for children, parents, and teachers — stewarded by Svarna Gauranga Das.",
    siteName: "Bhāva",
    type: "website",
  },
  other: { "theme-color": "#061628" },
};

const nav = [
  ["Home", "/"],
  ["Library", "/library"],
  ["For Teachers", "/teachers"],
  ["Prabhupāda Vāṇī", "/prabhupada-vani"],
  ["Bhakti Blog", "/blog"],
  ["About", "/about"],
  ["Contact", "/contact"],
];

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${display.variable} ${body.variable}`}>
      <body>
        <div className="site-shell">
          <header className="site-header">
            <div className="container header-inner">
              <Link href="/" className="brand-lockup" aria-label="Bhāva home">
                <span className="brand-mark" aria-hidden="true">❀</span>
                <span>
                  <span className="wordmark">bh<span>ā</span>va</span>
                  <span className="brand-sub">Devotional learning</span>
                </span>
              </Link>
              <nav className="nav" aria-label="Primary navigation">
                {nav.map(([label, href]) => (
                  <Link key={href} href={href}>{label}</Link>
                ))}
              </nav>
            </div>
          </header>
          <main>{children}</main>
          <footer className="site-footer">
            <div className="container footer-inner">
              <span>Bhāva — stewarded with care by Svarna Gauranga Das.</span>
              <div className="footer-links">
                <Link href="/privacy">Privacy</Link>
                <Link href="/accessibility">Accessibility</Link>
                <Link href="/source-permissions">Source & permissions</Link>
                <Link href="/studio">Factory Studio</Link>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
