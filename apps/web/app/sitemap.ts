import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = "https://bhava.me";
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
    "/blog",
    "/about",
    "/contact",
    "/privacy",
    "/accessibility",
    "/source-permissions",
  ];
  const cantos = Array.from({ length: 12 }, (_, i) => `/library/srimad-bhagavatam/canto/${i + 1}`);
  const stories = Array.from({ length: 7 }, (_, index) => `/stories/${String(index + 1).padStart(3, "0")}`);
  return [...staticRoutes, ...cantos, ...stories].map((path) => ({
    url: `${base}${path}`,
    lastModified: new Date(),
  }));
}
