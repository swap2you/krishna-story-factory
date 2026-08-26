const VANI_AUDIO = /^\/api\/v1\/vani\/(?:[a-z0-9_-]+\/)+audio\/?$/i;

export function isAllowlistedAudioUrl(url: string, origin = "http://127.0.0.1"): boolean {
  try {
    const parsed = new URL(url, origin);
    if (parsed.origin !== new URL(origin).origin) return false;
    return /narration\.mp3$/i.test(parsed.pathname) || VANI_AUDIO.test(parsed.pathname);
  } catch {
    return false;
  }
}
