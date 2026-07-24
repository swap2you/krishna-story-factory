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

export function SiteHeader() {
  const pathname = usePathname() || "/";
  const [open, setOpen] = useState(false);
  const [learningOpen, setLearningOpen] = useState(false);
  const learningId = useId();
  const learningRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    setOpen(false);
    setLearningOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (!learningOpen) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setLearningOpen(false);
    };
    const onClick = (event: MouseEvent) => {
      if (!learningRef.current?.contains(event.target as Node)) setLearningOpen(false);
    };
    window.addEventListener("keydown", onKey);
    window.addEventListener("mousedown", onClick);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("mousedown", onClick);
    };
  }, [learningOpen]);

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

          <div className="nav-learning" ref={learningRef}>
            <button
              type="button"
              className="nav-learning__button"
              aria-expanded={learningOpen}
              aria-controls={learningId}
              onClick={() => setLearningOpen((value) => !value)}
            >
              Learning
            </button>
            <div id={learningId} className={`nav-learning__menu ${learningOpen ? "is-open" : ""}`} hidden={!learningOpen}>
              {learningLinks.map((item) => (
                <Link key={item.href} href={item.href} onClick={() => setLearningOpen(false)}>
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
