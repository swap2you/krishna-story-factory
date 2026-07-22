import type { Metadata } from "next";
import { Fraunces, Source_Sans_3 } from "next/font/google";
import Link from "next/link";
import "@bhava/ui/styles.css";
import "./globals.css";

const display = Fraunces({ subsets: ["latin"], variable: "--font-display" });
const body = Source_Sans_3({ subsets: ["latin"], variable: "--font-body" });

export const metadata: Metadata = {
  title: { default: "Bhāva — Stories for the heart", template: "%s | Bhāva" },
  description: "A gentle devotional learning home for Krishna stories and family practice.",
};

const nav = [["Home", "/"], ["Library", "/library"], ["For Teachers", "/teachers"], ["Prabhupāda Vāṇī", "/vanani"], ["Bhakti Blog", "/blog"], ["About", "/about"], ["Contact", "/contact"]];

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en" className={`${display.variable} ${body.variable}`}><body><div className="site-shell">
    <header className="site-header"><div className="container header-inner"><Link href="/" className="wordmark">bh<span>ā</span>va</Link><nav className="nav" aria-label="Primary navigation">{nav.map(([label, href]) => <Link key={href} href={href}>{label}</Link>)}</nav></div></header>
    <main>{children}</main>
    <footer className="site-footer"><div className="container footer-inner"><span>Bhāva — devotional learning with care.</span><div className="footer-links"><Link href="/privacy">Privacy</Link><Link href="/accessibility">Accessibility</Link><Link href="/source-permissions">Source & permissions</Link><Link href="/studio">Factory Studio</Link></div></div></footer>
  </div></body></html>;
}
