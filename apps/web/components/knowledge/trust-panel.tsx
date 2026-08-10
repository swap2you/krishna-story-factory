"use client";

import Link from "next/link";
import type { ReactNode, SyntheticEvent } from "react";

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
  return (
    <section className={`knowledge-source ${className || ""}`.trim()} aria-label="Source and review">
      <details
        className="knowledge-source-details"
        {...(controlled
          ? {
              open,
              onToggle: (e: SyntheticEvent<HTMLDetailsElement>) => {
                onOpenChange?.((e.target as HTMLDetailsElement).open);
              },
            }
          : { open: defaultOpen || undefined })}
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
