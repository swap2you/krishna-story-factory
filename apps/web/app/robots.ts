import type { MetadataRoute } from "next";
import { CANONICAL_ORIGIN } from "@/lib/seo";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: [
        "/studio",
        "/studio/",
        "/dev",
        "/dev/",
        "/api/studio",
        "/api/studio/",
        "/api/v1/factory",
        "/api/v1/scheduler",
        "/api/v1/queue",
        "/work",
        "/staging",
        "/output/_archive",
        "/stories/010",
      ],
    },
    sitemap: `${CANONICAL_ORIGIN}/sitemap.xml`,
    host: CANONICAL_ORIGIN,
  };
}
