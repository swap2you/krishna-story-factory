import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getStory, getStories } from "@/lib/catalog";
import { StoryExperience } from "@/components/story-experience";
import { PUBLIC_STORY_MAX } from "@/lib/public-boundary";
import {
  AUTHOR_NAME,
  PUBLISHER_NAME,
  absoluteUrl,
  pageMetadata,
} from "@/lib/seo";

export const dynamic = "force-dynamic";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ storyNo: string }>;
}): Promise<Metadata> {
  const { storyNo } = await params;
  const digits = storyNo.replace(/\D/g, "");
  const numeric = Number.parseInt(digits, 10);
  if (!digits || !Number.isFinite(numeric) || numeric < 1 || numeric > PUBLIC_STORY_MAX) {
    return pageMetadata({
      title: `Story ${storyNo} — unpublished`,
      description: "This Bhāva story is not publicly released.",
      path: `/stories/${storyNo}`,
      noIndex: true,
    });
  }

  const padded = String(numeric).padStart(3, "0");
  const story = await getStory(padded).catch(() => null);
  if (!story) {
    return pageMetadata({
      title: `Story ${padded} — in preparation`,
      description: "This Bhāva story is not publicly released.",
      path: `/stories/${padded}`,
      noIndex: true,
    });
  }

  return pageMetadata({
    title: `${story.title} — Krishna story for children`,
    description:
      story.source_reference ||
      `Listen to and read Bhāva Krishna Book Story ${story.story_no}, with devotional activities for children and families.`,
    path: `/stories/${story.story_no}`,
    image: story.poster_url || undefined,
  });
}

export default async function StoryPage({ params }: { params: Promise<{ storyNo: string }> }) {
  const { storyNo } = await params;
  if (!/^[a-z0-9-]+$/i.test(storyNo)) notFound();

  const numeric = Number.parseInt(storyNo.replace(/\D/g, ""), 10);
  if (!Number.isFinite(numeric) || numeric < 1 || numeric > PUBLIC_STORY_MAX) notFound();

  let story = null;
  let maxReleased = 0;
  try {
    const stories = await getStories();
    maxReleased = stories.reduce((max, item) => {
      const value = Number.parseInt(String(item.story_no || ""), 10);
      return Number.isFinite(value) ? Math.max(max, value) : max;
    }, 0);
    story = await getStory(storyNo);
  } catch {
    /* The shell remains available if the API is briefly unavailable. */
  }

  if (!story) notFound();

  const canonical = absoluteUrl(`/stories/${story.story_no}`);
  const articleJsonLd = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: story.title,
    description:
      story.source_reference ||
      `Bhāva Krishna Book story ${story.story_no} for children and families.`,
    mainEntityOfPage: canonical,
    url: canonical,
    image: story.poster_url ? absoluteUrl(story.poster_url) : undefined,
    inLanguage: "en",
    isFamilyFriendly: true,
    author: { "@type": "Person", name: AUTHOR_NAME },
    publisher: { "@type": "Organization", name: PUBLISHER_NAME },
    educationalUse: ["reading", "listening", "devotional education"],
    audio: story.narration_url
      ? {
          "@type": "AudioObject",
          contentUrl: absoluteUrl(story.narration_url),
          encodingFormat: "audio/mpeg",
          name: `${story.title} narration`,
        }
      : undefined,
  };

  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Bhāva", item: absoluteUrl("/") },
      {
        "@type": "ListItem",
        position: 2,
        name: "Krishna Book",
        item: absoluteUrl("/library/krishna-book"),
      },
      { "@type": "ListItem", position: 3, name: story.title, item: canonical },
    ],
  };

  return (
    <div className="story-shell">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(articleJsonLd).replace(/</g, "\\u003c") }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd).replace(/</g, "\\u003c") }}
      />
      <aside className="story-sidebar">
        <Link
          href="/library/krishna-book"
          className="bhava-button bhava-button--quiet"
          style={{ color: "#fff", borderColor: "rgba(255,255,255,.25)" }}
        >
          ← Krishna Book
        </Link>
        {story.poster_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={story.poster_url}
            alt={`${story.title} — illustrated Krishna story poster`}
            width={720}
            height={900}
            decoding="async"
          />
        ) : null}
        <p className="source-pill">Story {story.story_no}</p>
        <h2>{story.title}</h2>
        <p>{story.age_range ? `Suggested for ${story.age_range}` : "For children and families."}</p>
        <p>{story.source_reference}</p>
        <Link
          href="/library/krishna-book/how-to-use"
          className="sidebar-how-to"
        >
          <span className="sidebar-how-to__icon" aria-hidden="true">
            ✦
          </span>
          How to use these stories
        </Link>
      </aside>
      <section className="story-main">
        <div className="story-top">
          <div>
            <p className="eyebrow">Listen · Read · Activities</p>
            <h1>{story.title}</h1>
          </div>
        </div>
        <StoryExperience
          story={story}
          storyNo={story.story_no}
          maxReleased={Math.min(maxReleased || PUBLIC_STORY_MAX, PUBLIC_STORY_MAX)}
        />
      </section>
    </div>
  );
}
