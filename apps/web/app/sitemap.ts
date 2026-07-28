import type { MetadataRoute } from "next";

const PUBLIC_STORY_COUNT = 9;

export default function sitemap(): MetadataRoute.Sitemap {
  const base = process.env.BHAVA_CANONICAL_ORIGIN?.replace(/\/$/, "") || "https://bhava.me";
  const staticRoutes = [
    "",
    "/library",
    "/library/krishna-book",
    "/library/srimad-bhagavatam",
    "/library/bhagavad-gita",
    "/library/ramayana",
    "/library/rama-katha",
    "/library/ramacaritamanasa",
    "/library/dasavatara",
    "/library/caitanya-caritamrta",
    "/library/caitanya-bhagavata",
    "/library/prayers-mantras",
    "/library/teacher-resources",
    "/teachers",
    "/sunday-school",
    "/preachers",
    "/prabhupada-vani",
    "/knowledge",
    "/knowledge/topics",
    "/knowledge/questions",
    "/knowledge/prayers",
    "/knowledge/slokas",
    "/knowledge/search",
    "/faq",
    "/printables",
    "/about",
    "/contact",
    "/privacy",
    "/accessibility",
    "/source-permissions",
    "/rights",
  ];
  const cantos = Array.from({ length: 12 }, (_, i) => `/library/srimad-bhagavatam/canto/${i + 1}`);
  // Governed published catalog for launch: Stories 001–009 only. Story 010 stays excluded.
  const stories = Array.from(
    { length: PUBLIC_STORY_COUNT },
    (_, index) => `/stories/${String(index + 1).padStart(3, "0")}`,
  );
  const privatePrefixes = ["/studio", "/dev", "/api/studio"];
  const paths = [...staticRoutes, ...cantos, ...stories].filter(
    (path) => !privatePrefixes.some((prefix) => path === prefix || path.startsWith(`${prefix}/`)),
  );
  return paths.map((path) => ({
    url: `${base}${path}`,
    lastModified: new Date(),
  }));
}
