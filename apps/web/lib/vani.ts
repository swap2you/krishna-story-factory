export const VANI_COLLECTION_ID = "krishna-book";
export const VANI_COLLECTION_PATH = "/prabhupada-vani/krishna-book";
export const VANI_STORAGE_PREFIX = "bhava:vani";

export type VaniAvailability = "available" | "unavailable";

export type VaniTrack = {
  id: string;
  chapterStart: number | null;
  chapterEnd: number | null;
  title: string;
  description: string | null;
  availability: VaniAvailability;
  durationSeconds: number | null;
  audioUrl: string | null;
  waveformUrl: string | null;
  sourceTitle: string | null;
  sourceUrl: string | null;
  transcriptUrl: string | null;
  relatedStoryId: string | null;
  restored: boolean;
  downloadAllowed: boolean;
};

export type VaniCollection = {
  id: string;
  title: string;
  description: string | null;
  tracks: VaniTrack[];
};

export type VaniLoadState<T> =
  | { status: "ok"; data: T }
  | { status: "unavailable" };

export type VaniProgress = {
  position: number;
  duration: number;
  updatedAt: number;
};

export type VaniFilter = "all" | "available" | "unavailable" | "bookmarked" | "completed";

const API =
  process.env.BHAVA_API_URL ??
  (process.env.BHAVA_API_ORIGIN
    ? `${process.env.BHAVA_API_ORIGIN.replace(/\/$/, "")}/api/v1`
    : "http://127.0.0.1:8000/api/v1");

function record(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};
}

function text(...values: unknown[]): string | null {
  const value = values.find((item) => typeof item === "string" && item.trim());
  return typeof value === "string" ? value.trim() : null;
}

function numberOrNull(...values: unknown[]): number | null {
  const value = values.find((item) => typeof item === "number" || (typeof item === "string" && item.trim()));
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : null;
}

function bool(...values: unknown[]): boolean {
  return values.some((value) => value === true);
}

function sameOriginMediaUrl(value: unknown): string | null {
  if (typeof value !== "string" || !value.trim()) return null;
  const url = value.trim();
  if (url.startsWith("/")) return url;
  try {
    const parsed = new URL(url);
    if (parsed.hostname === "127.0.0.1" || parsed.hostname === "localhost") {
      return `${parsed.pathname}${parsed.search}`;
    }
  } catch {
    return url.startsWith("api/") ? `/${url}` : null;
  }
  return null;
}

export function normalizeVaniTrack(value: unknown): VaniTrack | null {
  const item = record(value);
  const source = record(item.source);
  const restored = record(item.restored);
  const rights = record(item.rights);
  const transcript = record(item.transcript);
  const related = Array.isArray(item.related_story_ids) ? item.related_story_ids : [];
  const id = text(item.canonical_track_id, item.track_id, item.id, item.slug);
  const title = text(item.canonical_title, item.title, item.source_title);
  if (!id || !title) return null;
  const rawAvailability = text(item.availability, item.status)?.toLowerCase();
  const audioUrl = sameOriginMediaUrl(
    item.audio_url ?? item.stream_url ?? restored.audio_url ?? restored.url,
  );
  const available = rawAvailability === "available" || (!rawAvailability && Boolean(audioUrl));
  return {
    id,
    chapterStart: numberOrNull(item.chapter_start, item.chapter, item.chapter_number),
    chapterEnd: numberOrNull(item.chapter_end),
    title,
    description: text(item.description, item.context, item.summary),
    availability: available && audioUrl ? "available" : "unavailable",
    durationSeconds: numberOrNull(
      item.duration_seconds,
      restored.duration_seconds,
      record(item.original).duration_seconds,
    ),
    audioUrl: available ? audioUrl : null,
    waveformUrl: sameOriginMediaUrl(item.waveform_url ?? restored.waveform_url),
    sourceTitle: text(source.title, item.source_title),
    sourceUrl: text(source.page_url, item.source_url),
    transcriptUrl: text(transcript.url, item.transcript_url),
    relatedStoryId: text(item.related_story_id, related[0]),
    restored: bool(item.restored_listening_edition, restored.sha256, restored.relative_path),
    downloadAllowed: bool(item.download_allowed, rights.public_download_allowed),
  };
}

export function normalizeVaniCollection(value: unknown): VaniCollection {
  const body = record(value);
  const rawTracks = Array.isArray(value)
    ? value
    : Array.isArray(body.tracks)
      ? body.tracks
      : Array.isArray(body.items)
        ? body.items
        : [];
  return {
    id: text(body.collection_id, body.id, body.slug) ?? VANI_COLLECTION_ID,
    title: text(body.title) ?? "Krishna Book Dictation Archive",
    description: text(body.description),
    tracks: rawTracks
      .map(normalizeVaniTrack)
      .filter((track): track is VaniTrack => track !== null)
      .sort(compareVaniTracks),
  };
}

export function compareVaniTracks(a: VaniTrack, b: VaniTrack): number {
  const chapterA = a.chapterStart ?? (a.id === "00" ? 0 : Number(a.id.replace(/\D/g, "")));
  const chapterB = b.chapterStart ?? (b.id === "00" ? 0 : Number(b.id.replace(/\D/g, "")));
  return (Number.isFinite(chapterA) ? chapterA : 999) - (Number.isFinite(chapterB) ? chapterB : 999);
}

export function filterVaniTracks(
  tracks: VaniTrack[],
  query: string,
  filter: VaniFilter,
  bookmarked: ReadonlySet<string> = new Set(),
  completed: ReadonlySet<string> = new Set(),
): VaniTrack[] {
  const needle = query.trim().toLocaleLowerCase();
  return tracks.filter((track) => {
    const chapter = track.chapterStart == null ? "" : String(track.chapterStart);
    if (needle && !`${track.id} ${chapter} ${track.title}`.toLocaleLowerCase().includes(needle)) return false;
    if (filter === "available") return track.availability === "available";
    if (filter === "unavailable") return track.availability === "unavailable";
    if (filter === "bookmarked") return bookmarked.has(track.id);
    if (filter === "completed") return completed.has(track.id);
    return true;
  });
}

export function adjacentAvailableTracks(tracks: VaniTrack[], trackId: string) {
  const available = tracks.filter((track) => track.availability === "available" && track.audioUrl);
  const index = available.findIndex((track) => track.id === trackId);
  return {
    previous: index > 0 ? available[index - 1] : null,
    next: index >= 0 && index < available.length - 1 ? available[index + 1] : null,
  };
}

export function formatVaniDuration(seconds: number | null): string {
  if (seconds == null || !Number.isFinite(seconds) || seconds < 0) return "Duration unavailable";
  const total = Math.round(seconds);
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const remainder = total % 60;
  return hours > 0
    ? `${hours}:${String(minutes).padStart(2, "0")}:${String(remainder).padStart(2, "0")}`
    : `${minutes}:${String(remainder).padStart(2, "0")}`;
}

async function apiGet(path: string): Promise<unknown | null> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 4000);
  try {
    const response = await fetch(`${API}${path}`, { cache: "no-store", signal: controller.signal });
    return response.ok ? await response.json() : null;
  } catch {
    return null;
  } finally {
    clearTimeout(timer);
  }
}

export async function loadVaniCollection(): Promise<VaniLoadState<VaniCollection>> {
  const body = await apiGet("/vani/krishna-book");
  if (body == null) return { status: "unavailable" };
  return { status: "ok", data: normalizeVaniCollection(body) };
}

export async function loadVaniTrack(trackId: string): Promise<VaniLoadState<VaniTrack>> {
  const safeId = trackId.trim();
  if (!/^[a-zA-Z0-9_-]+$/.test(safeId)) return { status: "unavailable" };
  const body = await apiGet(`/vani/krishna-book/${encodeURIComponent(safeId)}`);
  const track = body == null ? null : normalizeVaniTrack(body);
  if (track) return { status: "ok", data: track };
  const collection = await loadVaniCollection();
  const fallback =
    collection.status === "ok"
      ? collection.data.tracks.find((item) => item.id === safeId)
      : null;
  return fallback ? { status: "ok", data: fallback } : { status: "unavailable" };
}
