"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const LAST_STORY_KEY = "bhava:last-story";

export function ContinueJourney() {
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
          className="bhava-button bhava-button--quiet hero-secondary-cta"
          href="/library/krishna-book"
        >
          Browse all stories
        </Link>
      </div>
      <Link
        href="/library/krishna-book/how-to-use"
        className="hero-journey-chip"
        data-testid="hero-journey-chip"
      >
        <span className="hero-journey-chip__icon" aria-hidden="true">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <path
              d="M5 7h14M5 12h10M5 17h7"
              stroke="currentColor"
              strokeWidth="2.2"
              strokeLinecap="round"
            />
            <circle cx="18" cy="17" r="3" fill="currentColor" opacity="0.85" />
          </svg>
        </span>
        <span className="hero-journey-chip__label">
          See the five-step family journey
        </span>
      </Link>
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
