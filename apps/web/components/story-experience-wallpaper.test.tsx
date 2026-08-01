import { render } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { Story } from "@/lib/catalog";
import { StoryExperience } from "./story-experience";
import { StoryGrid } from "./story-grid";

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    ...rest
  }: {
    children: React.ReactNode;
    href: string;
    className?: string;
  }) => (
    <a href={href} {...rest}>
      {children}
    </a>
  ),
}));

vi.mock("@/components/audio-player", () => ({
  AudioPlayer: ({ onAudioMount }: { onAudioMount?: (el: HTMLAudioElement) => void }) => {
    const { useEffect } = require("react") as typeof import("react");
    useEffect(() => {
      const audio = document.createElement("audio");
      Object.defineProperty(audio, "paused", { value: true, configurable: true });
      Object.defineProperty(audio, "currentTime", { value: 0, configurable: true, writable: true });
      Object.defineProperty(audio, "duration", { value: 120, configurable: true, writable: true });
      onAudioMount?.(audio);
    }, [onAudioMount]);
    return <div className="audio-player" data-testid="audio-player" />;
  },
}));

vi.mock("@/components/pdf-js-viewer", () => ({
  PdfJsViewer: () => null,
}));

const mockStory: Story = {
  story_no: "001",
  slug: "001-prayers",
  title: "Prayers of the Demigods",
  poster_url: "/media/stories/001/story_poster.png",
  narration_url: "/media/stories/001/narration.mp3",
  simple_coloring_url: "/media/stories/001/simple_coloring_page.png",
  coloring_url: "/media/stories/001/coloring_page.png",
  activity_pdf_url: "/media/stories/001/activity_sheet.pdf",
};

function mockStoryFetch() {
  global.fetch = vi.fn((input: RequestInfo | URL) => {
    const path = String(input);
    if (path.includes("/reader")) {
      return Promise.resolve({
        ok: true,
        text: () => Promise.resolve("# Story\n\nBody text for wallpaper test."),
      } as Response);
    }
    if (path.includes("/web-manifest")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({}),
      } as Response);
    }
    if (path.includes("/sync")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ status: "needs_alignment", cues: [] }),
      } as Response);
    }
    if (path.includes("/source-links") || path.includes("/reflections")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve([]),
      } as Response);
    }
    if (path.includes("/shlokas")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ shlokas: [], status: "pending" }),
      } as Response);
    }
    return Promise.resolve({ ok: false } as Response);
  }) as typeof fetch;
}

beforeEach(() => {
  mockStoryFetch();
  localStorage.clear();

  class MockIntersectionObserver {
    observe = vi.fn();
    disconnect = vi.fn();
    constructor(_cb: IntersectionObserverCallback) {}
  }
  vi.stubGlobal("IntersectionObserver", MockIntersectionObserver);

  class MockResizeObserver {
    observe = vi.fn();
    disconnect = vi.fn();
  }
  vi.stubGlobal("ResizeObserver", MockResizeObserver);
});

describe("StoryExperience wallpaper", () => {
  it("renders story-poster-wash with the catalog poster img src", () => {
    const { container } = render(<StoryExperience story={mockStory} storyNo="001" maxReleased={20} />);

    const wash = container.querySelector(".story-poster-wash");
    expect(wash).not.toBeNull();
    expect(wash?.getAttribute("data-poster-src")).toBe(mockStory.poster_url);

    const img = wash?.querySelector("img");
    expect(img?.getAttribute("src")).toBe(mockStory.poster_url);
    expect(img?.getAttribute("alt")).toBe("");
  });

  it("omits story-poster-wash when poster_url is missing", () => {
    const { container } = render(
      <StoryExperience story={{ ...mockStory, poster_url: null }} storyNo="001" maxReleased={20} />,
    );

    expect(container.querySelector(".story-poster-wash")).toBeNull();
  });
});

describe("StoryGrid wallpaper boundary (home / library grids)", () => {
  it("does not render story-poster-wash on catalog story grids", () => {
    const { container } = render(
      <StoryGrid stories={[{ story_no: "001", slug: "001", title: "Story One", age_range: "5–9" }]} />,
    );

    expect(container.querySelector(".story-poster-wash")).toBeNull();
  });
});
