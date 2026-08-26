import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import { VaniTrackPlayer } from "@/components/vani/vani-player";
import {
  VANI_COLLECTION_PATH,
  adjacentAvailableTracks,
  formatVaniDuration,
  loadVaniCollection,
  loadVaniTrack,
} from "@/lib/vani";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Krishna Book Dictation",
  robots: { index: false, follow: false },
};

export default async function VaniTrackPage({ params }: { params: Promise<{ trackId: string }> }) {
  const { trackId } = await params;
  const [trackState, collectionState] = await Promise.all([
    loadVaniTrack(trackId),
    loadVaniCollection(),
  ]);
  if (trackState.status !== "ok") {
    return (
      <>
        <PageIntro eyebrow="Prabhupāda Vāṇī" title="Recording not found." body="This archive entry is unavailable or has not cleared private review." />
        <section className="section" style={{ paddingTop: 0 }}>
          <div className="container"><Link href={VANI_COLLECTION_PATH}>← Return to the ordered catalog</Link></div>
        </section>
      </>
    );
  }
  const track = trackState.data;
  const adjacent = collectionState.status === "ok"
    ? adjacentAvailableTracks(collectionState.data.tracks, track.id)
    : { previous: null, next: null };
  const chapterLabel = track.id === "00"
    ? "Introduction · Track 00"
    : `Chapter ${track.chapterStart ?? track.id}${track.chapterEnd && track.chapterEnd !== track.chapterStart ? `–${track.chapterEnd}` : ""}`;
  return (
    <>
      <PageIntro
        eyebrow={`Krishna Book Dictation · ${chapterLabel}`}
        title={track.title}
        body={track.description ?? "A source-preserving listening page for this Krishna Book dictation."}
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container vani-detail">
          <nav className="vani-breadcrumb" aria-label="Breadcrumb">
            <Link href="/prabhupada-vani">Prabhupāda Vāṇī</Link><span aria-hidden="true">/</span>
            <Link href={VANI_COLLECTION_PATH}>Krishna Book</Link><span aria-hidden="true">/</span><span>{chapterLabel}</span>
          </nav>
          <div className="vani-detail-grid">
            <div>
              <VaniTrackPlayer
                track={{
                  ...track,
                  previousId: adjacent.previous?.id,
                  nextId: adjacent.next?.id,
                }}
              />
            </div>
            <aside className="vani-provenance" aria-labelledby="recording-notes">
              <p className="eyebrow">Recording notes</p>
              <h2 id="recording-notes">Provenance & care</h2>
              <dl>
                <div><dt>Status</dt><dd>{track.availability === "available" ? "Available to listen" : "Recording unavailable"}</dd></div>
                <div><dt>Edition</dt><dd>{track.restored ? "Restored listening edition" : "Source listening edition"}</dd></div>
                <div><dt>Duration</dt><dd>{formatVaniDuration(track.durationSeconds)}</dd></div>
                <div><dt>Source</dt><dd>{track.sourceUrl ? <a href={track.sourceUrl} rel="noreferrer">View {track.sourceTitle ?? "source record"}</a> : "Source record retained; public link unavailable"}</dd></div>
              </dl>
              <p className="hint">
                “Restored listening edition” means conservative processing was used to improve listening
                clarity while preserving the historical recording. It does not mean “true HD.”
              </p>
              {track.transcriptUrl ? <p><a href={track.transcriptUrl} rel="noreferrer">Read the authorized text alternative</a></p> : (
                <p className="hint">An authorized transcript is not linked for this recording.</p>
              )}
              {track.relatedStoryId ? (
                <p><Link href={`/stories/${track.relatedStoryId}`}>Open related Bhāva story →</Link></p>
              ) : null}
              {track.downloadAllowed && track.audioUrl ? (
                <p><a href={track.audioUrl} download>Download permitted audio</a></p>
              ) : null}
            </aside>
          </div>
        </div>
      </section>
    </>
  );
}
