/**
 * Single source of truth for collection readiness status.
 * Used by Home, Library, CollectionCard callers, and header menus.
 *
 * Active = usable public content exists today.
 * Planned = page exists but content is taxonomy-only or coming soon.
 */

export type CollectionStatus = "active" | "planned";

export interface CollectionEntry {
  slug: string;
  status: CollectionStatus;
  title: string;
  href: string;
  description: string;
}

const READINESS: Record<string, CollectionStatus> = {
  "krishna-book": "active",
  knowledge: "active",
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

export const ACTIVE_AREAS: CollectionEntry[] = [
  {
    slug: "krishna-book",
    status: "active",
    href: "/library/krishna-book",
    title: "Krishna Book Stories",
    description: "Published bedtime packages with audio and printables.",
  },
  {
    slug: "knowledge",
    status: "active",
    href: "/knowledge",
    title: "Knowledge Library",
    description: "Governed pathways, questions, and reviewed guides.",
  },
  {
    slug: "printables",
    status: "active",
    href: "/printables",
    title: "Printables",
    description: "Posters, coloring, and activity sheets from real packages.",
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
    description: "Class packs and classroom pathways.",
  },
  {
    slug: "prabhupada-vani",
    status: "planned",
    href: "/prabhupada-vani",
    title: "Prabhupāda Vāṇī",
    description: "Source-governed taxonomy for future reviewed records.",
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
] as const;
