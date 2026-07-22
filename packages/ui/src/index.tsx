"use client";

import { type ButtonHTMLAttributes, type ReactNode, useEffect, useId, useState } from "react";

export function Button({ variant = "primary", className = "", ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "accent" | "quiet" }) {
  return <button className={`bhava-button bhava-button--${variant} ${className}`} {...props} />;
}

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`bhava-card ${className}`}>{children}</section>;
}

export function Tabs({ tabs, children }: { tabs: string[]; children: (active: string) => ReactNode }) {
  const [active, setActive] = useState(tabs[0]);
  return <div><div className="bhava-tabs" role="tablist">{tabs.map((tab) => <button key={tab} className="bhava-tab" role="tab" aria-selected={active === tab} onClick={() => setActive(tab)}>{tab}</button>)}</div><div role="tabpanel">{children(active)}</div></div>;
}

export function Dialog({ open, title, children, onClose }: { open: boolean; title: string; children: ReactNode; onClose: () => void }) {
  const id = useId();
  if (!open) return null;
  return <div role="presentation" className="bhava-dialog-backdrop" onMouseDown={onClose}><section role="dialog" aria-modal="true" aria-labelledby={id} className="bhava-dialog" onMouseDown={(event) => event.stopPropagation()}><div><h2 id={id}>{title}</h2><Button variant="quiet" aria-label="Close dialog" onClick={onClose}>Close</Button></div>{children}</section></div>;
}

export function Tooltip({ label, children }: { label: string; children: ReactNode }) {
  return <span className="bhava-tooltip" aria-label={label}>{children}<span role="tooltip">{label}</span></span>;
}

export function Toast({ message }: { message: string | null }) {
  return message ? <output className="bhava-toast" aria-live="polite">{message}</output> : null;
}

export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`bhava-skeleton ${className}`} aria-label="Loading content" />;
}

export function EmptyState({ title = "Nothing here yet", children }: { title?: string; children?: ReactNode }) {
  return <div className="bhava-state"><h2>{title}</h2>{children}</div>;
}

export function ErrorState({ title = "We could not load this right now", children }: { title?: string; children?: ReactNode }) {
  return <div className="bhava-state" role="alert"><h2>{title}</h2>{children}</div>;
}

export function LoadingState({ label = "Loading…" }: { label?: string }) {
  return <div className="bhava-state" aria-live="polite"><Skeleton className="bhava-loading-dot" /><p>{label}</p></div>;
}

export function useToast() {
  const [message, setMessage] = useState<string | null>(null);
  useEffect(() => { if (!message) return; const timer = window.setTimeout(() => setMessage(null), 3000); return () => window.clearTimeout(timer); }, [message]);
  return { message, showToast: setMessage };
}
