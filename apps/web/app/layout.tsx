import type { Metadata } from "next";
import { Fraunces, Source_Sans_3, Tillana } from "next/font/google";
import "@bhava/ui/styles.css";
import "./globals.css";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import {
  AUTHOR_NAME,
  CANONICAL_ORIGIN,
  CONTACT_EMAIL,
  PUBLISHER_NAME,
  SEO_TOPICS,
  SITE_NAME,
  absoluteUrl,
} from "@/lib/seo";

const brandDisplay = Tillana({
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  variable: "--font-brand-display",
});
const display = Fraunces({ subsets: ["latin"], variable: "--font-display" });
const body = Source_Sans_3({ subsets: ["latin"], variable: "--font-body" });

export const metadata: Metadata = {
  metadataBase: new URL(CANONICAL_ORIGIN),
  title: {
    default: "Bhāva — Krishna stories, scripture and devotional learning",
    template: "%s | Bhāva",
  },
  description:
    "Bona fide Krishna stories, scripture learning, audio, activities, coloring pages and teacher resources for children, families and devotional communities.",
  applicationName: SITE_NAME,
  authors: [{ name: AUTHOR_NAME, url: absoluteUrl("/about") }],
  creator: AUTHOR_NAME,
  publisher: PUBLISHER_NAME,
  keywords: SEO_TOPICS,
  alternates: { canonical: "/" },
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
    title: "Bhāva — Krishna stories and devotional learning",
    description:
      "Stories, scripture, audio and learning resources for children, families and teachers.",
    siteName: SITE_NAME,
    type: "website",
    url: "/",
    images: [
      {
        url: "/og/bhava-share-1200x630.webp",
        width: 1200,
        height: 630,
        alt: "Bhāva — Krishna stories, scripture and devotional learning",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Bhāva — Krishna stories and devotional learning",
    description:
      "Stories, scripture, audio and learning resources for children, families and teachers.",
    images: ["/og/bhava-share-1200x630.webp"],
  },
  verification: {
    google: process.env.GOOGLE_SITE_VERIFICATION || undefined,
    other: process.env.BING_SITE_VERIFICATION
      ? { "msvalidate.01": process.env.BING_SITE_VERIFICATION }
      : undefined,
  },
  category: "education",
  other: {
    "theme-color": "#061628",
    "contact": CONTACT_EMAIL,
    "rights": absoluteUrl("/rights"),
  },
};

const organizationJsonLd = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: SITE_NAME,
  alternateName: "Bhava",
  url: CANONICAL_ORIGIN,
  logo: absoluteUrl("/brand/logo-primary-horizontal.webp"),
  founder: { "@type": "Person", name: AUTHOR_NAME },
  email: `mailto:${CONTACT_EMAIL}`,
  address: {
    "@type": "PostalAddress",
    addressLocality: "Harrisburg",
    addressRegion: "PA",
    addressCountry: "US",
  },
  publishingPrinciples: absoluteUrl("/rights"),
};

const websiteJsonLd = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: SITE_NAME,
  alternateName: "Bhava",
  url: CANONICAL_ORIGIN,
  inLanguage: "en",
  publisher: { "@type": "Organization", name: PUBLISHER_NAME },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${brandDisplay.variable} ${display.variable} ${body.variable}`}>
      <body>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationJsonLd).replace(/</g, "\\u003c") }}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(websiteJsonLd).replace(/</g, "\\u003c") }}
        />
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
