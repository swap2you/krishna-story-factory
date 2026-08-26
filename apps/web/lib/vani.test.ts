import { describe, expect, it } from "vitest";
import {
  adjacentAvailableTracks,
  filterVaniTracks,
  formatVaniDuration,
  normalizeVaniCollection,
  type VaniTrack,
} from "./vani";

const tracks: VaniTrack[] = [
  {
    id: "00",
    chapterStart: 0,
    chapterEnd: null,
    title: "Introduction",
    description: null,
    availability: "available",
    durationSeconds: 65,
    audioUrl: "/api/v1/vani/krishna-book/00/audio",
    waveformUrl: null,
    sourceTitle: null,
    sourceUrl: null,
    transcriptUrl: null,
    relatedStoryId: null,
    restored: true,
    downloadAllowed: false,
  },
  { ...({} as VaniTrack), ...{
    id: "01", chapterStart: 1, chapterEnd: null, title: "The Advent of Lord Krishna",
    description: null, availability: "unavailable" as const, durationSeconds: null, audioUrl: null,
    waveformUrl: null, sourceTitle: null, sourceUrl: null, transcriptUrl: null,
    relatedStoryId: null, restored: false, downloadAllowed: false,
  } },
  { ...({} as VaniTrack), ...{
    id: "02", chapterStart: 2, chapterEnd: null, title: "Prayers by the Demigods",
    description: null, availability: "available" as const, durationSeconds: 120, audioUrl: "/api/v1/vani/krishna-book/02/audio",
    waveformUrl: null, sourceTitle: null, sourceUrl: null, transcriptUrl: null,
    relatedStoryId: null, restored: true, downloadAllowed: false,
  } },
];

describe("Vāṇī catalog helpers", () => {
  it("normalizes and orders API records", () => {
    const collection = normalizeVaniCollection({
      items: [
        { canonical_track_id: "02", canonical_title: "Two", chapter_start: 2, availability: "available", audio_url: "/api/v1/vani/krishna-book/02/audio" },
        { canonical_track_id: "00", canonical_title: "Introduction", chapter_start: 0, availability: "unavailable" },
      ],
    });
    expect(collection.tracks.map((track) => track.id)).toEqual(["00", "02"]);
    expect(collection.tracks[1].availability).toBe("available");
  });

  it("searches and filters without making unavailable tracks playable", () => {
    expect(filterVaniTracks(tracks, "advent", "all").map((track) => track.id)).toEqual(["01"]);
    expect(filterVaniTracks(tracks, "", "unavailable").map((track) => track.id)).toEqual(["01"]);
    expect(filterVaniTracks(tracks, "", "bookmarked", new Set(["02"])).map((track) => track.id)).toEqual(["02"]);
  });

  it("finds adjacent available tracks across a gap", () => {
    const adjacent = adjacentAvailableTracks(tracks, "00");
    expect(adjacent.previous).toBeNull();
    expect(adjacent.next?.id).toBe("02");
  });

  it("formats short and long durations", () => {
    expect(formatVaniDuration(65)).toBe("1:05");
    expect(formatVaniDuration(3661)).toBe("1:01:01");
    expect(formatVaniDuration(null)).toBe("Duration unavailable");
  });
});
