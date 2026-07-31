"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useId, useRef, useState } from "react";

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

function isActive(pathname: string, href: string) {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

function learningPathActive(pathname: string) {
  return learningLinks.some((item) => isActive(pathname, item.href));
}

export function SiteHeader() {
  const pathname = usePathname() || "/";
  const [open, setOpen] = useState(false);
  const [learningOpen, setLearningOpen] = useState(false);
  const learningId = useId();
  const learningRef = useRef<HTMLDivElement | null>(null);
  const hoverCloseTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearHoverClose = () => {
    if (hoverCloseTimer.current) {
      clearTimeout(hoverCloseTimer.current);
      hoverCloseTimer.current = null;
    }
  };

  const openLearning = () => {
    clearHoverClose();
    setLearningOpen(true);
  };

  const scheduleCloseLearning = () => {
    clearHoverClose();
    hoverCloseTimer.current = setTimeout(() => setLearningOpen(false), 180);
  };

  useEffect(() => {
    setOpen(false);
    setLearningOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (!learningOpen) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setLearningOpen(false);
    };
    const onPointerDown = (event: PointerEvent) => {
      if (!learningRef.current?.contains(event.target as Node)) setLearningOpen(false);
    };
    window.addEventListener("keydown", onKey);
    window.addEventListener("pointerdown", onPointerDown);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("pointerdown", onPointerDown);
    };
  }, [learningOpen]);

  useEffect(() => () => clearHoverClose(), []);

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
            className={`nav-learning ${learningOpen ? "is-open" : ""}`}
            ref={learningRef}
            onMouseEnter={openLearning}
            onMouseLeave={scheduleCloseLearning}
            onFocusCapture={openLearning}
            onBlurCapture={(event) => {
              const next = event.relatedTarget as Node | null;
              if (!learningRef.current?.contains(next)) setLearningOpen(false);
            }}
          >
            <button
              type="button"
              className="nav-learning__button"
              aria-expanded={learningOpen}
              aria-controls={learningId}
              aria-haspopup="true"
              onClick={() => {
                // Desktop: hover may already open the menu; a click must not toggle it closed.
                // Mobile accordion: click toggles open/closed.
                const mobile =
                  typeof window !== "undefined" && window.matchMedia("(max-width: 720px)").matches;
                setLearningOpen((was) => (mobile ? !was : true));
              }}
            >
              Learning
            </button>
            <div
              id={learningId}
              className={`nav-learning__menu ${learningOpen ? "is-open" : ""}`}
              hidden={!learningOpen}
              role="group"
              aria-label="Learning links"
            >
              {learningLinks.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-current={isActive(pathname, item.href) ? "page" : undefined}
                  onClick={() => {
                    setLearningOpen(false);
                    setOpen(false);
                  }}
                >
                  {item.label}
                </Link>
              ))}
            </div>
            {learningPathActive(pathname) ? <span className="sr-only">Learning section active</span> : null}
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
