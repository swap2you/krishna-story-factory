"use client";

import { useState } from "react";

/** Local-only usefulness signal — never a popularity feed. */
export function HelpfulVote({ resourceId }: { resourceId: string }) {
  const key = `bhava:helpful:${resourceId}`;
  const [value, setValue] = useState<string | null>(() => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(key);
  });

  function vote(next: "yes" | "no") {
    localStorage.setItem(key, next);
    setValue(next);
  }

  return (
    <div className="helpful-vote" aria-label="Was this helpful?">
      <span className="hint">Was this helpful?</span>{" "}
      <button type="button" className="bhava-button bhava-button--quiet" onClick={() => vote("yes")} aria-pressed={value === "yes"}>
        Helpful
      </button>
      <button type="button" className="bhava-button bhava-button--quiet" onClick={() => vote("no")} aria-pressed={value === "no"}>
        Not helpful
      </button>
      {value ? <span className="hint"> Saved on this device only.</span> : null}
    </div>
  );
}
