"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useCallback, useEffect, useId, useRef, useState, type KeyboardEvent as ReactKeyboardEvent } from "react";

const primary = [
  { label: "Home", href: "/" },
  { label: "Library", href: "/library" },
  { label: "Knowledge", href: "/knowledge" },
] as const;

const learningLinks = [
  { label: "Children & Youth", href: "/learning/children-youth" },
  { label: "Sunday School", href: "/sunday-school" },
  { label: "For Teachers", href: "/teachers" },
  { label: "For Preachers", href: "/preachers" },
  { label: "Printables", href: "/printables" },
] as const;

const trailing = [
  { label: "Prabhupāda Vāṇī", href: "/prabhupada-vani" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
] as const;

const HOVER_CLOSE_DELAY_MS = 150;
const HOVER_OPEN_DELAY_MS = 220;

function isActive(pathname: string, href: string) {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

function prefersFineHover() {
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") return false;
  return window.matchMedia("(hover: hover) and (pointer: fine)").matches;
}

export function SiteHeader() {
  const pathname = usePathname() || "/";
  const [open, setOpen] = useState(false);
  const [learningOpen, setLearningOpen] = useState(false);
  const learningId = useId();
  const learningRef = useRef<HTMLDivElement | null>(null);
  const learningButtonRef = useRef<HTMLButtonElement | null>(null);
  const hoverCloseTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const hoverOpenTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearHoverTimers = useCallback(() => {
    if (hoverCloseTimer.current) {
      clearTimeout(hoverCloseTimer.current);
      hoverCloseTimer.current = null;
    }
    if (hoverOpenTimer.current) {
      clearTimeout(hoverOpenTimer.current);
      hoverOpenTimer.current = null;
    }
  }, []);

  const closeLearning = useCallback(
    (restoreFocus = false) => {
      clearHoverTimers();
      setLearningOpen(false);
      if (restoreFocus) {
        learningButtonRef.current?.focus();
      }
    },
    [clearHoverTimers],
  );

  const openLearning = useCallback(() => {
    clearHoverTimers();
    setLearningOpen(true);
  }, [clearHoverTimers]);

  useEffect(() => {
    setOpen(false);
    closeLearning(false);
  }, [pathname, closeLearning]);

  useEffect(() => {
    if (!learningOpen) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        closeLearning(true);
      }
    };
    const onPointerDown = (event: PointerEvent) => {
      if (!learningRef.current?.contains(event.target as Node)) {
        closeLearning(false);
      }
    };
    window.addEventListener("keydown", onKey);
    window.addEventListener("pointerdown", onPointerDown);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("pointerdown", onPointerDown);
    };
  }, [learningOpen, closeLearning]);

  useEffect(() => () => clearHoverTimers(), [clearHoverTimers]);

  const onLearningClick = () => {
    // Click/tap is authoritative and synchronous relative to delayed hover-open.
    clearHoverTimers();
    setLearningOpen((value) => !value);
  };

  const onLearningKeyDown = (event: ReactKeyboardEvent<HTMLButtonElement>) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      onLearningClick();
    }
  };

  const onLearningMouseEnter = () => {
    if (!prefersFineHover()) return;
    clearHoverTimers();
    // Delay hover-open so a real click is never raced by an immediate mouseenter open.
    hoverOpenTimer.current = setTimeout(() => {
      setLearningOpen(true);
    }, HOVER_OPEN_DELAY_MS);
  };

  const onLearningMouseLeave = () => {
    if (!prefersFineHover()) return;
    clearHoverTimers();
    hoverCloseTimer.current = setTimeout(() => {
      const root = learningRef.current;
      if (root?.contains(document.activeElement)) return;
      setLearningOpen(false);
    }, HOVER_CLOSE_DELAY_MS);
  };

  const onLearningFocusCapture = () => {
    clearHoverTimers();
  };

  return (
    <header className="site-header">
      <div className="container header-inner">
        <Link href="/" className="brand-lockup" aria-label="Bhāva home">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            className="brand-mark"
            src="/brand/logo-icon-only.webp"
            alt=""
            width={44}
            height={44}
            aria-hidden="true"
          />
          <span className="brand-text">
            <span className="wordmark brand-display">Bhāva</span>
            <span className="brand-sub">Devotional learning</span>
          </span>
        </Link>

        <button
          type="button"
          className="nav-toggle"
          aria-expanded={open}
          aria-controls="primary-nav"
          onClick={() => setOpen((value) => !value)}
        >
          Menu
        </button>

        <nav id="primary-nav" className={`nav ${open ? "nav--open" : ""}`} aria-label="Primary navigation">
          {primary.map((item) => (
            <Link key={item.href} href={item.href} aria-current={isActive(pathname, item.href) ? "page" : undefined}>
              {item.label}
            </Link>
          ))}

          <div
            className="nav-learning"
            ref={learningRef}
            data-state={learningOpen ? "open" : "closed"}
            onMouseEnter={onLearningMouseEnter}
            onMouseLeave={onLearningMouseLeave}
            onFocusCapture={onLearningFocusCapture}
          >
            <button
              type="button"
              ref={learningButtonRef}
              className="nav-learning__button"
              aria-expanded={learningOpen}
              aria-controls={learningId}
              aria-haspopup="true"
              onClick={onLearningClick}
              onKeyDown={onLearningKeyDown}
            >
              Learning
            </button>
            <div
              id={learningId}
              className="nav-learning__menu"
              data-state={learningOpen ? "open" : "closed"}
              role="group"
              aria-label="Learning links"
            >
              {learningLinks.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-current={isActive(pathname, item.href) ? "page" : undefined}
                  onClick={() => closeLearning(false)}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>

          {trailing.map((item) => (
            <Link key={item.href} href={item.href} aria-current={isActive(pathname, item.href) ? "page" : undefined}>
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
