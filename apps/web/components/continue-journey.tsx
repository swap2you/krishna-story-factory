"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const LAST_STORY_KEY = "bhava:last-story";

type LatestStory = {
  story_no: string;
  title: string;
  poster_url?: string | null;
};

export function ContinueJourney({
  latestStory,
}: {
  latestStory: LatestStory | null;
}) {
  const [lastStoryNo, setLastStoryNo] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    try {
      const raw = localStorage.getItem(LAST_STORY_KEY);
      if (raw) {
        const parsed = JSON.parse(raw) as { storyNo?: string };
        if (parsed?.storyNo) {
          setLastStoryNo(parsed.storyNo);
          return;
        }
      }
      let highest: string | null = null;
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (!key) continue;
        const match = key.match(
          /^bhava:(?:notes|bookmark|resume):(\d{3})$/,
        );
        if (match && localStorage.getItem(key)) {
          const candidate = match[1];
          if (!highest || candidate > highest) highest = candidate;
        }
      }
      if (highest) setLastStoryNo(highest);
    } catch {
      /* private mode */
    }
  }, []);

  const hasProgress = mounted && !!lastStoryNo;
  const showLatest =
    latestStory && latestStory.story_no !== lastStoryNo;

  return (
    <div className="continue-journey-inner">
      <div
        className="continue-journey-primary"
        data-testid="home-story-primary-ctas"
      >
        {hasProgress ? (
          <Link
            className="bhava-button bhava-button--accent"
            href={`/stories/${lastStoryNo}`}
          >
            Continue Story {lastStoryNo}
          </Link>
        ) : (
          <Link
            className="bhava-button bhava-button--accent"
            href="/stories/001"
          >
            Begin with Story 001
          </Link>
        )}
        <Link
          className="bhava-button bhava-button--quiet"
          href="/library/krishna-book"
        >
          Browse all stories
        </Link>
      </div>
      <p className="hero-text-link">
        <Link href="/library/krishna-book/how-to-use">
          How the weekly journey works
        </Link>
      </p>
      {showLatest ? (
        <p className="continue-journey-latest hint">
          Latest published:{" "}
          <Link href={`/stories/${latestStory.story_no}`}>
            Story {latestStory.story_no} &mdash; {latestStory.title}
          </Link>
        </p>
      ) : null}
    </div>
  );
}

export function writeLastStory(storyNo: string, tab?: string) {
  try {
    localStorage.setItem(
      LAST_STORY_KEY,
      JSON.stringify({ storyNo, tab, ts: Date.now() }),
    );
  } catch {
    /* private mode */
  }
}
