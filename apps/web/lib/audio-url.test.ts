import { describe, expect, it } from "vitest";
import { isAllowlistedAudioUrl } from "./audio-url";

describe("audio URL allowlist", () => {
  const origin = "https://bhava.example";

  it("keeps story narration playback allowed", () => {
    expect(isAllowlistedAudioUrl("/api/v1/stories/025/assets/narration.mp3", origin)).toBe(true);
  });

  it("allows same-origin Vāṇī streaming endpoints", () => {
    expect(isAllowlistedAudioUrl("/api/v1/vani/krishna-book/00/audio", origin)).toBe(true);
  });

  it("rejects cross-origin and unrelated resources", () => {
    expect(isAllowlistedAudioUrl("https://media.example/api/v1/vani/krishna-book/00/audio", origin)).toBe(false);
    expect(isAllowlistedAudioUrl("/api/v1/vani/krishna-book/00/manifest", origin)).toBe(false);
  });
});
