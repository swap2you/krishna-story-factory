import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = "https://bhava.me";
  const staticRoutes = ["", "/library", "/library/krishna-book", "/teachers", "/vanani", "/blog", "/about", "/contact", "/privacy", "/accessibility", "/source-permissions"];
  const stories = Array.from({ length: 7 }, (_, index) => `/stories/${String(index + 1).padStart(3, "0")}`);
  return [...staticRoutes, ...stories].map((path) => ({
    url: `${base}${path}`,
    lastModified: new Date(),
  }));
}
