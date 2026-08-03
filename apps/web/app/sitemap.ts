import type { MetadataRoute } from "next";
import { PUBLIC_STORY_MAX } from "@/lib/public-boundary";
import { CANONICAL_ORIGIN } from "@/lib/seo";

export default function sitemap(): MetadataRoute.Sitemap {
  const staticRoutes = [
    "",
    "/library",
    "/library/krishna-book",
    "/library/krishna-book/how-to-use",
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
  const cantos = Array.from(
    { length: 12 },
    (_, index) => `/library/srimad-bhagavatam/canto/${index + 1}`,
  );
  const stories = Array.from(
    { length: PUBLIC_STORY_MAX },
    (_, index) => `/stories/${String(index + 1).padStart(3, "0")}`,
  );

  const now = new Date();
  return [...staticRoutes, ...cantos, ...stories].map((path) => ({
    url: `${CANONICAL_ORIGIN}${path}`,
    lastModified: now,
    changeFrequency: path.startsWith("/stories/") ? "monthly" : "weekly",
    priority: path === "" ? 1 : path.startsWith("/stories/") ? 0.8 : 0.6,
  }));
}
