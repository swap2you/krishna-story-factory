/**
 * Single source of truth for collection readiness status.
 * Used by Home, Library, CollectionCard callers, and header menus.
 *
 * Active = usable public content exists today.
 * Planned = page exists but content is taxonomy-only or coming soon.
 */

import { PUBLIC_STORY_MAX } from "@/lib/public-boundary";

export type CollectionStatus = "active" | "planned";

const STORY_CEILING = String(PUBLIC_STORY_MAX).padStart(3, "0");

export interface CollectionEntry {
  slug: string;
  status: CollectionStatus;
  title: string;
  href: string;
  description: string;
}

const READINESS: Record<string, CollectionStatus> = {
  "krishna-book": "active",
  library: "active",
  knowledge: "active",
  learning: "active",
  printables: "active",
  "teacher-resources": "planned",
  "srimad-bhagavatam": "planned",
  "bhagavad-gita": "planned",
  ramayana: "planned",
  "rama-katha": "planned",
  ramacaritamanasa: "planned",
  dasavatara: "planned",
  "caitanya-caritamrta": "planned",
  "caitanya-bhagavata": "planned",
  "prayers-mantras": "planned",
  "sunday-school": "planned",
  "prabhupada-vani": "planned",
  "devotee-lives": "planned",
};

export function getCollectionStatus(slug: string): CollectionStatus {
  return READINESS[slug] ?? "planned";
}

export function isCollectionActive(slug: string): boolean {
  return getCollectionStatus(slug) === "active";
}

/** Four public pillars shown on Home — honest status labels. */
export const ACTIVE_AREAS: CollectionEntry[] = [
  {
    slug: "library",
    status: "active",
    href: "/library",
    title: "Library",
    description: `Krishna Book Stories 001–${STORY_CEILING} with audio, text, and printables.`,
  },
  {
    slug: "knowledge",
    status: "active",
    href: "/knowledge",
    title: "Knowledge",
    description: "Source-led guides, pathways, and reviewed Q&A — not a random blog.",
  },
  {
    slug: "learning",
    status: "active",
    href: "/learning",
    title: "Learning",
    description:
      "Pathways for children, families, Sunday School, teachers, preachers, Gurukula/homeschool, and festival use.",
  },
  {
    slug: "prabhupada-vani",
    status: "planned",
    href: "/prabhupada-vani",
    title: "Prabhupāda Vāṇī",
    description: "Governed teaching surface — taxonomy ready; curated records later.",
  },
];

export const GROWING_NEXT: CollectionEntry[] = [
  {
    slug: "prayers-mantras",
    status: "planned",
    href: "/library/prayers-mantras",
    title: "Prayers & Ślokas",
    description: "Planned prayer and mantra learning spaces.",
  },
  {
    slug: "sunday-school",
    status: "planned",
    href: "/sunday-school",
    title: "Sunday School",
    description: "Weekly planning structure for age groups.",
  },
  {
    slug: "teacher-resources",
    status: "planned",
    href: "/teachers",
    title: "Teacher Resources",
    description: "Class packs and classroom pathways still growing.",
  },
  {
    slug: "srimad-bhagavatam",
    status: "planned",
    href: "/library/srimad-bhagavatam",
    title: "Śrīmad-Bhāgavatam",
    description: "Canto shelves prepared; stories not released yet.",
  },
  {
    slug: "devotee-lives",
    status: "planned",
    href: "/library",
    title: "Devotee Lives",
    description: "Bhaktamāla / lives of devotees — planned with care.",
  },
];

/** Library mega-menu groups for the site header. */
export const LIBRARY_MENU_BOOKS = [
  { slug: "krishna-book", href: "/library/krishna-book", label: "Krishna Book" },
  { slug: "srimad-bhagavatam", href: "/library/srimad-bhagavatam", label: "Śrīmad-Bhāgavatam" },
  { slug: "bhagavad-gita", href: "/library/bhagavad-gita", label: "Bhagavad-gītā" },
  { slug: "ramayana", href: "/library/ramayana", label: "Rāmāyaṇa" },
  { slug: "rama-katha", href: "/library/rama-katha", label: "Rāma-kathā" },
  { slug: "ramacaritamanasa", href: "/library/ramacaritamanasa", label: "Rāmacaritamānasa" },
  { slug: "dasavatara", href: "/library/dasavatara", label: "Daśāvatāra" },
  { slug: "caitanya-caritamrta", href: "/library/caitanya-caritamrta", label: "Caitanya-caritāmṛta" },
  { slug: "caitanya-bhagavata", href: "/library/caitanya-bhagavata", label: "Caitanya-bhāgavata" },
] as const;

export const LIBRARY_MENU_PRACTICE = [
  { slug: "prayers-mantras", href: "/library/prayers-mantras", label: "Prayers & Mantras" },
  { slug: "printables", href: "/printables", label: "Printables" },
] as const;

export const LIBRARY_MENU_EDUCATOR = [
  { slug: "teacher-resources", href: "/teachers", label: "Teacher Resources" },
  { slug: "knowledge", href: "/knowledge", label: "Knowledge Library" },
  { slug: "learning", href: "/learning", label: "Learning Hub" },
] as const;
