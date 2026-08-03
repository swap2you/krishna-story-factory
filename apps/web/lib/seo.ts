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

export const DEFAULT_OG_IMAGE = "/og/bhava-share-1200x630.webp";
export const DEFAULT_OG_WIDTH = 1200;
export const DEFAULT_OG_HEIGHT = 630;

export function pageMetadata(input: {
  title: string;
  description: string;
  path: string;
  image?: string;
  imageWidth?: number;
  imageHeight?: number;
  noIndex?: boolean;
}): Metadata {
  const canonical = absoluteUrl(input.path);
  const image = absoluteUrl(input.image || DEFAULT_OG_IMAGE);
  const imgWidth = input.imageWidth ?? (input.image ? undefined : DEFAULT_OG_WIDTH);
  const imgHeight = input.imageHeight ?? (input.image ? undefined : DEFAULT_OG_HEIGHT);
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
      images: [{ url: image, alt: input.title, width: imgWidth, height: imgHeight }],
    },
    twitter: {
      card: "summary_large_image",
      title: input.title,
      description: input.description,
      images: [image],
    },
  };
}
