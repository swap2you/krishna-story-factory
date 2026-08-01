"use client";

import {
  forwardRef,
  type ButtonHTMLAttributes,
  type KeyboardEvent,
  type ReactNode,
  useEffect,
  useId,
  useRef,
  useState,
} from "react";

export const Button = forwardRef<
  HTMLButtonElement,
  ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "accent" | "quiet" }
>(function Button({ variant = "primary", className = "", ...props }, ref) {
  return <button ref={ref} className={`bhava-button bhava-button--${variant} ${className}`} {...props} />;
});

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`bhava-card ${className}`}>{children}</section>;
}

export function Tabs({ tabs, children }: { tabs: string[]; children: (active: string) => ReactNode }) {
  const [active, setActive] = useState(tabs[0]);
  const baseId = useId();
  const tabRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const activeIndex = Math.max(0, tabs.indexOf(active));

  const selectIndex = (index: number) => {
    const nextIndex = ((index % tabs.length) + tabs.length) % tabs.length;
    setActive(tabs[nextIndex]);
    queueMicrotask(() => tabRefs.current[nextIndex]?.focus());
  };

  const onTabKeyDown = (event: KeyboardEvent<HTMLButtonElement>, index: number) => {
    if (event.key === "ArrowRight") {
      event.preventDefault();
      selectIndex(index + 1);
    } else if (event.key === "ArrowLeft") {
      event.preventDefault();
      selectIndex(index - 1);
    } else if (event.key === "Home") {
      event.preventDefault();
      selectIndex(0);
    } else if (event.key === "End") {
      event.preventDefault();
      selectIndex(tabs.length - 1);
    }
  };

  return (
    <div>
      <div className="bhava-tabs" role="tablist" aria-label="Story sections">
        {tabs.map((tab, index) => {
          const tabId = `${baseId}-tab-${index}`;
          const panelId = `${baseId}-panel-${index}`;
          const selected = active === tab;
          return (
            <button
              key={tab}
              id={tabId}
              ref={(el) => {
                tabRefs.current[index] = el;
              }}
              className="bhava-tab"
              role="tab"
              type="button"
              aria-selected={selected}
              aria-controls={panelId}
              tabIndex={selected ? 0 : -1}
              onClick={() => setActive(tab)}
              onKeyDown={(event) => onTabKeyDown(event, index)}
            >
              {tab}
            </button>
          );
        })}
      </div>
      <div
        id={`${baseId}-panel-${activeIndex}`}
        role="tabpanel"
        aria-labelledby={`${baseId}-tab-${activeIndex}`}
      >
        {children(active)}
      </div>
    </div>
  );
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
