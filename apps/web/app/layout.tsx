import type { Metadata } from "next";
import { Fraunces, Source_Sans_3, Tillana } from "next/font/google";
import "@bhava/ui/styles.css";
import "./globals.css";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";

/** Licensed/open Google fonts — Samarkan webfont slot reserved via --font-brand-display. */
const brandDisplay = Tillana({
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  variable: "--font-brand-display",
});
const display = Fraunces({ subsets: ["latin"], variable: "--font-display" });
const body = Source_Sans_3({ subsets: ["latin"], variable: "--font-body" });

export const metadata: Metadata = {
  title: { default: "Bhāva — Timeless devotion for growing hearts and minds", template: "%s | Bhāva" },
  description:
    "Stories, scripture, practice, and learning paths for children, youth, families, and teachers.",
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
    description: "Timeless devotion for growing hearts and minds.",
    siteName: "Bhāva",
    type: "website",
  },
  other: { "theme-color": "#061628" },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${brandDisplay.variable} ${display.variable} ${body.variable}`}>
      <body>
        <div className="site-shell">
          <a className="skip-link" href="#main-content">Skip to content</a>
          <SiteHeader />
          <main id="main-content">{children}</main>
          <SiteFooter />
        </div>
      </body>
    </html>
  );
}
