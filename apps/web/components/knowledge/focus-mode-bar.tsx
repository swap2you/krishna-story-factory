"use client";

type Props = {
  focusMode: boolean;
  onToggle: () => void;
  /** Multi-stanza package controls; omit for article soft-focus. */
  stanzaNav?: {
    index: number;
    total: number;
    onPrev: () => void;
    onNext: () => void;
  };
};

/** Template V1 focus-mode controls (keyboard-safe stanza stepping when provided). */
export function FocusModeBar({ focusMode, onToggle, stanzaNav }: Props) {
  return (
    <div className="knowledge-focus-bar">
      <button type="button" className="bhava-button" aria-pressed={focusMode} onClick={onToggle}>
        {focusMode ? "Exit focus mode" : "Focus mode"}
      </button>
      {focusMode && stanzaNav ? (
        <>
          <button
            type="button"
            className="bhava-button"
            disabled={stanzaNav.index <= 0}
            onClick={stanzaNav.onPrev}
          >
            Previous stanza
          </button>
          <button
            type="button"
            className="bhava-button"
            disabled={stanzaNav.index >= stanzaNav.total - 1}
            onClick={stanzaNav.onNext}
          >
            Next stanza
          </button>
        </>
      ) : null}
    </div>
  );
}
