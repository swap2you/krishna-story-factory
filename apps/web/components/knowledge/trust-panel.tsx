"use client";

import Link from "next/link";
import { useState, type ReactNode, type SyntheticEvent } from "react";

export type TrustPanelRow = {
  label: string;
  value: ReactNode;
};

type Props = {
  rows: TrustPanelRow[];
  /** Controlled open state (Study lens default). */
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  /** Uncontrolled initial open when `open` is omitted. */
  defaultOpen?: boolean;
  className?: string;
};

/**
 * Template V1 trust panel — sources, rights/use, version, review, correction route.
 * Presentational; callers decide which fields are honest/available.
 */
export function TrustPanel({ rows, open, onOpenChange, defaultOpen = false, className }: Props) {
  const controlled = open !== undefined;
  const [uncontrolledOpen, setUncontrolledOpen] = useState(defaultOpen);
  const isOpen = controlled ? Boolean(open) : uncontrolledOpen;

  return (
    <section className={`knowledge-source ${className || ""}`.trim()} aria-label="Source and review">
      <details
        className="knowledge-source-details"
        open={isOpen}
        onToggle={(e: SyntheticEvent<HTMLDetailsElement>) => {
          const next = (e.target as HTMLDetailsElement).open;
          if (controlled) {
            onOpenChange?.(next);
          } else {
            setUncontrolledOpen(next);
          }
        }}
      >
        <summary>Source and review</summary>
        <dl>
          {rows.map((row) => (
            <div key={row.label}>
              <dt>{row.label}</dt>
              <dd>{row.value}</dd>
            </div>
          ))}
        </dl>
        <p>
          <Link href="/knowledge/corrections">Request a correction</Link>
        </p>
      </details>
    </section>
  );
}
