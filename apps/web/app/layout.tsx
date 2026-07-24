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
  icons: {
    icon: [
      { url: "/favicon.svg", type: "image/svg+xml" },
      { url: "/favicon-32.png", sizes: "32x32", type: "image/png" },
      { url: "/brand/logo-icon-only.webp", type: "image/webp" },
      { url: "/brand/icon-512.svg", sizes: "512x512", type: "image/svg+xml" },
    ],
    apple: [{ url: "/brand/icon-192.svg", sizes: "192x192", type: "image/svg+xml" }],
  },
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
  ["Knowledge", "/knowledge"],
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
                {/* Desktop/tablet: approved small-header wordmark at true aspect (not icon crop). */}
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  className="brand-logo-header"
                  src="/brand/logo-small-header.webp"
                  alt="bhāva"
                  width={220}
                  height={32}
                />
                {/* Mobile: approved icon mark + live typography (macron preserved). */}
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  className="brand-mark-mobile"
                  src="/brand/logo-icon-only.webp"
                  alt=""
                  width={40}
                  height={40}
                  aria-hidden="true"
                />
                <span className="brand-text-mobile">
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
              <div className="footer-brand">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  className="brand-logo-footer"
                  src="/brand/logo-dark-bg.webp"
                  alt="bhāva"
                  width={160}
                  height={61}
                />
                <span>Stewarded with care by Svarna Gauranga Das · Harrisburg, Pennsylvania</span>
              </div>
              <div className="footer-links">
                <Link href="/sunday-school">Sunday School</Link>
                <Link href="/preachers">For Preachers</Link>
                <Link href="/faq">FAQ</Link>
                <Link href="/printables">Printables</Link>
                <Link href="/privacy">Privacy</Link>
                <Link href="/accessibility">Accessibility</Link>
                <Link href="/source-permissions">Source & permissions</Link>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
