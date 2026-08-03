"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useCallback, useEffect, useId, useRef, useState, type KeyboardEvent as ReactKeyboardEvent } from "react";
import {
  getCollectionStatus,
  LIBRARY_MENU_BOOKS,
  LIBRARY_MENU_PRACTICE,
  LIBRARY_MENU_EDUCATOR,
} from "@/lib/collection-readiness";

const primary = [
  { label: "Home", href: "/" },
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

function useDropdown() {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement | null>(null);
  const buttonRef = useRef<HTMLButtonElement | null>(null);
  const hoverClose = useRef<ReturnType<typeof setTimeout> | null>(null);
  const hoverOpen = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearTimers = useCallback(() => {
    if (hoverClose.current) { clearTimeout(hoverClose.current); hoverClose.current = null; }
    if (hoverOpen.current) { clearTimeout(hoverOpen.current); hoverOpen.current = null; }
  }, []);

  const close = useCallback((restoreFocus = false) => {
    clearTimers();
    setOpen(false);
    if (restoreFocus) buttonRef.current?.focus();
  }, [clearTimers]);

  const toggle = useCallback(() => {
    clearTimers();
    setOpen((v) => !v);
  }, [clearTimers]);

  const onMouseEnter = useCallback(() => {
    if (!prefersFineHover()) return;
    clearTimers();
    hoverOpen.current = setTimeout(() => setOpen(true), HOVER_OPEN_DELAY_MS);
  }, [clearTimers]);

  const onMouseLeave = useCallback(() => {
    if (!prefersFineHover()) return;
    clearTimers();
    hoverClose.current = setTimeout(() => {
      if (ref.current?.contains(document.activeElement)) return;
      setOpen(false);
    }, HOVER_CLOSE_DELAY_MS);
  }, [clearTimers]);

  useEffect(() => () => clearTimers(), [clearTimers]);

  return { open, setOpen, ref, buttonRef, close, toggle, onMouseEnter, onMouseLeave, clearTimers };
}

export function SiteHeader() {
  const pathname = usePathname() || "/";
  const [mobileOpen, setMobileOpen] = useState(false);

  const library = useDropdown();
  const learning = useDropdown();
  const libraryId = useId();
  const learningId = useId();

  useEffect(() => {
    setMobileOpen(false);
    library.close(false);
    learning.close(false);
  }, [pathname, library.close, learning.close]);

  useEffect(() => {
    if (!library.open && !learning.open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        if (library.open) library.close(true);
        if (learning.open) learning.close(true);
      }
    };
    const onPointer = (e: PointerEvent) => {
      if (library.open && !library.ref.current?.contains(e.target as Node)) library.close(false);
      if (learning.open && !learning.ref.current?.contains(e.target as Node)) learning.close(false);
    };
    window.addEventListener("keydown", onKey);
    window.addEventListener("pointerdown", onPointer);
    return () => { window.removeEventListener("keydown", onKey); window.removeEventListener("pointerdown", onPointer); };
  }, [
    library.open,
    learning.open,
    library.close,
    learning.close,
    library.ref,
    learning.ref,
  ]);

  const onKeyDown = (dd: ReturnType<typeof useDropdown>) => (e: ReactKeyboardEvent<HTMLButtonElement>) => {
    if (e.key === "Enter" || e.key === " ") { e.preventDefault(); dd.toggle(); }
  };

  return (
    <header className="site-header">
      <div className="container header-inner">
        <Link href="/" className="brand-lockup" aria-label="Bhāva home">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img className="brand-mark" src="/brand/logo-icon-only.webp" alt="" width={44} height={44} aria-hidden="true" />
          <span className="brand-text">
            <span className="wordmark brand-display">Bhāva</span>
            <span className="brand-sub">Devotional learning</span>
          </span>
        </Link>

        <button
          type="button"
          className="nav-toggle"
          aria-expanded={mobileOpen}
          aria-controls="primary-nav"
          onClick={() => setMobileOpen((v) => !v)}
        >
          Menu
        </button>

        <nav id="primary-nav" className={`nav ${mobileOpen ? "nav--open" : ""}`} aria-label="Primary navigation">
          {primary.map((item) => (
            <Link key={item.href} href={item.href} aria-current={isActive(pathname, item.href) ? "page" : undefined}>
              {item.label}
            </Link>
          ))}

          {/* ── Library mega-menu ──────────────────────── */}
          <div
            className="nav-dropdown nav-library"
            ref={library.ref}
            data-state={library.open ? "open" : "closed"}
            onMouseEnter={library.onMouseEnter}
            onMouseLeave={library.onMouseLeave}
            onFocusCapture={library.clearTimers}
          >
            <button
              type="button"
              ref={library.buttonRef}
              className="nav-dropdown__button"
              aria-expanded={library.open}
              aria-controls={libraryId}
              aria-haspopup="true"
              onClick={library.toggle}
              onKeyDown={onKeyDown(library)}
            >
              Library
            </button>
            <div
              id={libraryId}
              className="nav-dropdown__menu nav-library__menu"
              data-state={library.open ? "open" : "closed"}
              role="group"
              aria-label="Library links"
            >
              <div className="nav-mega-group">
                <Link
                  href="/library"
                  className="nav-mega-home"
                  aria-current={pathname === "/library" ? "page" : undefined}
                  onClick={() => library.close(false)}
                >
                  Library Home
                </Link>
              </div>
              <div className="nav-mega-group">
                <span className="nav-mega-label">Books &amp; Stories</span>
                {LIBRARY_MENU_BOOKS.map((item) => {
                  const status = getCollectionStatus(item.slug);
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      aria-current={isActive(pathname, item.href) ? "page" : undefined}
                      onClick={() => library.close(false)}
                    >
                      {item.label}
                      {status === "planned" ? <span className="nav-planned-badge">Planned</span> : null}
                    </Link>
                  );
                })}
              </div>
              <div className="nav-mega-group">
                <span className="nav-mega-label">Prayer &amp; Practice</span>
                {LIBRARY_MENU_PRACTICE.map((item) => {
                  const status = getCollectionStatus(item.slug);
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      aria-current={isActive(pathname, item.href) ? "page" : undefined}
                      onClick={() => library.close(false)}
                    >
                      {item.label}
                      {status === "planned" ? <span className="nav-planned-badge">Planned</span> : null}
                    </Link>
                  );
                })}
              </div>
              <div className="nav-mega-group">
                <span className="nav-mega-label">Educator Resources</span>
                {LIBRARY_MENU_EDUCATOR.map((item) => {
                  const status = getCollectionStatus(item.slug);
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      aria-current={isActive(pathname, item.href) ? "page" : undefined}
                      onClick={() => library.close(false)}
                    >
                      {item.label}
                      {status === "planned" ? <span className="nav-planned-badge">Planned</span> : null}
                    </Link>
                  );
                })}
              </div>
            </div>
          </div>

          {/* ── Learning mega-menu ──────────────────────── */}
          <div
            className="nav-dropdown nav-learning"
            ref={learning.ref}
            data-state={learning.open ? "open" : "closed"}
            onMouseEnter={learning.onMouseEnter}
            onMouseLeave={learning.onMouseLeave}
            onFocusCapture={learning.clearTimers}
          >
            <button
              type="button"
              ref={learning.buttonRef}
              className="nav-dropdown__button"
              aria-expanded={learning.open}
              aria-controls={learningId}
              aria-haspopup="true"
              onClick={learning.toggle}
              onKeyDown={onKeyDown(learning)}
            >
              Learning
            </button>
            <div
              id={learningId}
              className="nav-dropdown__menu nav-learning__menu"
              data-state={learning.open ? "open" : "closed"}
              role="group"
              aria-label="Learning links"
            >
              {learningLinks.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-current={isActive(pathname, item.href) ? "page" : undefined}
                  onClick={() => learning.close(false)}
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
