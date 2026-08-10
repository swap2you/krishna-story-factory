import type { MetadataRoute } from "next";
import { PUBLIC_STORY_MAX } from "@/lib/public-boundary";
import { CANONICAL_ORIGIN } from "@/lib/seo";
import { listPublicPilotCatalog } from "@/lib/knowledge/loader";
import { listPublicDerivativeMetas } from "@/lib/learning/derivatives";

export const runtime = "nodejs";

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
    "/learning",
    "/learning/children-youth",
    "/learning/families",
    "/learning/gurukula-homeschool",
    "/learning/festivals",
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

  const { guides, questions } = listPublicPilotCatalog();
  const knowledgeRoutes = [
    ...guides.map((g) => `/knowledge/${g.slug}`),
    ...questions.map((q) => `/knowledge/questions/${q.slug}`),
  ];
  const learningRoutes = listPublicDerivativeMetas().map(
    (d) => `/learning/derivatives/${d.slug}`,
  );

  const now = new Date();
  return [...staticRoutes, ...cantos, ...stories, ...knowledgeRoutes, ...learningRoutes].map(
    (path) => ({
      url: `${CANONICAL_ORIGIN}${path}`,
      lastModified: now,
      changeFrequency: path.startsWith("/stories/") ? "monthly" : "weekly",
      priority: path === "" ? 1 : path.startsWith("/stories/") ? 0.8 : 0.6,
    }),
  );
}
