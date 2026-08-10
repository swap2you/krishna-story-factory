"use client";

import type { LensId } from "@/lib/knowledge/package-types";
import { LENSES } from "@/lib/knowledge/package-types";

const LENS_LABELS: Record<LensId, string> = {
  little_learner: "Little Learner",
  explorer: "Explorer",
  teen: "Teen",
  study: "Study",
};

type Props = {
  lens: LensId;
  onSelect: (next: LensId, opts?: { restoreReadingFocus?: boolean }) => void;
  disabled?: boolean;
};

/** Template V1 lens radiogroup — Little Learner / Explorer / Teen / Study. */
export function LensSelector({ lens, onSelect, disabled }: Props) {
  return (
    <div
      className="knowledge-lens"
      role="radiogroup"
      aria-label="Reading depth lens"
      aria-disabled={disabled || undefined}
      onKeyDown={(e) => {
        if (disabled) return;
        const idx = LENSES.indexOf(lens);
        if (e.key === "ArrowRight" || e.key === "ArrowDown") {
          e.preventDefault();
          onSelect(LENSES[(idx + 1) % LENSES.length]);
        } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
          e.preventDefault();
          onSelect(LENSES[(idx - 1 + LENSES.length) % LENSES.length]);
        } else if (e.key === "Home") {
          e.preventDefault();
          onSelect(LENSES[0]);
        } else if (e.key === "End") {
          e.preventDefault();
          onSelect(LENSES[LENSES.length - 1]);
        }
      }}
    >
      {LENSES.map((id) => (
        <button
          key={id}
          type="button"
          role="radio"
          aria-checked={lens === id}
          tabIndex={lens === id ? 0 : -1}
          disabled={disabled}
          className={`bhava-button ${lens === id ? "bhava-button--primary knowledge-lens--selected" : ""}`}
          onClick={() => onSelect(id, { restoreReadingFocus: true })}
        >
          {LENS_LABELS[id]}
        </button>
      ))}
    </div>
  );
}

export { LENS_LABELS };
