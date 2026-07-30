import type { Metadata } from "next";

export const CANONICAL_ORIGIN =
  process.env.BHAVA_CANONICAL_ORIGIN?.replace(/\/$/, "") || "https://bhava.me";

export const SITE_NAME = "Bhāva";
export const AUTHOR_NAME = "Svarna Gauranga Das";
export const PUBLISHER_NAME = "Dauji Publication";
export const CONTACT_EMAIL = "svarnagaurangdas@gmail.com";

export const SEO_TOPICS = [
  "Krishna stories for children",
  "Krishna Book stories",
  "Bhagavad-gita learning",
  "Srimad Bhagavatam",
  "ISKCON children education",
  "Vaishnava Sunday school",
  "devotional activities for children",
  "bhakti learning for families",
  "Krishna coloring pages",
  "devotional printables",
];

export function absoluteUrl(path = "/"): string {
  return new URL(path, CANONICAL_ORIGIN).toString();
}

export function pageMetadata(input: {
  title: string;
  description: string;
  path: string;
  image?: string;
  noIndex?: boolean;
}): Metadata {
  const canonical = absoluteUrl(input.path);
  const image = absoluteUrl(input.image || "/heroes/hero-text-free-master-1280w.webp");
  return {
    title: input.title,
    description: input.description,
    alternates: { canonical },
    robots: input.noIndex
      ? { index: false, follow: false, noarchive: true }
      : { index: true, follow: true },
    openGraph: {
      type: "website",
      url: canonical,
      siteName: SITE_NAME,
      title: input.title,
      description: input.description,
      images: [{ url: image, alt: input.title }],
    },
    twitter: {
      card: "summary_large_image",
      title: input.title,
      description: input.description,
      images: [image],
    },
  };
}
