"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  useCallback,
  useEffect,
  useId,
  useRef,
  useState,
  type KeyboardEvent as ReactKeyboardEvent,
} from "react";
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
  { label: "Learning Hub", href: "/learning" },
  { label: "Children & Youth", href: "/learning/children-youth" },
  { label: "Families", href: "/learning/families" },
  { label: "Sunday School", href: "/sunday-school" },
  { label: "For Teachers", href: "/teachers" },
  { label: "For Preachers", href: "/preachers" },
  { label: "Gurukula / Homeschool", href: "/learning/gurukula-homeschool" },
  { label: "Festival use", href: "/learning/festivals" },
  { label: "Printables", href: "/printables" },
] as const;

const trailing = [
  { label: "Prabhupāda Vāṇī", href: "/prabhupada-vani" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
] as const;

type LibraryCategory = "home" | "books" | "practice" | "educator";

const LIBRARY_CATEGORIES: { id: LibraryCategory; label: string }[] = [
  { id: "home", label: "Library Home" },
  { id: "books", label: "Books & Stories" },
  { id: "practice", label: "Prayer & Practice" },
  { id: "educator", label: "Educator Resources" },
];

const HOVER_CLOSE_DELAY_MS = 160;
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
    if (hoverClose.current) {
      clearTimeout(hoverClose.current);
      hoverClose.current = null;
    }
    if (hoverOpen.current) {
      clearTimeout(hoverOpen.current);
      hoverOpen.current = null;
    }
  }, []);

  const close = useCallback(
    (restoreFocus = false) => {
      clearTimers();
      setOpen(false);
      if (restoreFocus) buttonRef.current?.focus();
    },
    [clearTimers],
  );

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

  return {
    open,
    setOpen,
    ref,
    buttonRef,
    close,
    toggle,
    onMouseEnter,
    onMouseLeave,
    clearTimers,
  };
}

function MenuLinks({
  items,
  pathname,
  onNavigate,
}: {
  items: readonly { slug: string; href: string; label: string }[];
  pathname: string;
  onNavigate: () => void;
}) {
  return (
    <>
      {items.map((item) => {
        const status = getCollectionStatus(item.slug);
        return (
          <Link
            key={item.href}
            href={item.href}
            aria-current={isActive(pathname, item.href) ? "page" : undefined}
            onClick={onNavigate}
          >
            {item.label}
            {status === "planned" ? (
              <span className="nav-planned-badge">Planned</span>
            ) : null}
          </Link>
        );
      })}
    </>
  );
}

export function SiteHeader() {
  const pathname = usePathname() || "/";
  const [mobileOpen, setMobileOpen] = useState(false);
  const [libraryCategory, setLibraryCategory] =
    useState<LibraryCategory>("books");
  const [mobileLibraryOpen, setMobileLibraryOpen] = useState(false);
  const [mobileLearningOpen, setMobileLearningOpen] = useState(false);
  const [mobileLibraryPanel, setMobileLibraryPanel] =
    useState<LibraryCategory | null>(null);

  const library = useDropdown();
  const learning = useDropdown();
  const libraryId = useId();
  const learningId = useId();
  const categoryPanelId = useId();

  useEffect(() => {
    setMobileOpen(false);
    setMobileLibraryOpen(false);
    setMobileLearningOpen(false);
    setMobileLibraryPanel(null);
    library.close(false);
    learning.close(false);
  }, [pathname, library.close, learning.close]);

  useEffect(() => {
    const anyOpen =
      library.open || learning.open || mobileLibraryOpen || mobileLearningOpen;
    if (!anyOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      e.preventDefault();
      if (library.open) library.close(true);
      if (learning.open) learning.close(true);
      if (mobileLibraryOpen) {
        setMobileLibraryOpen(false);
        setMobileLibraryPanel(null);
      }
      if (mobileLearningOpen) setMobileLearningOpen(false);
    };
    const onPointer = (e: PointerEvent) => {
      if (
        library.open &&
        !library.ref.current?.contains(e.target as Node)
      ) {
        library.close(false);
      }
      if (
        learning.open &&
        !learning.ref.current?.contains(e.target as Node)
      ) {
        learning.close(false);
      }
    };
    window.addEventListener("keydown", onKey);
    window.addEventListener("pointerdown", onPointer);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("pointerdown", onPointer);
    };
  }, [
    library.open,
    learning.open,
    mobileLibraryOpen,
    mobileLearningOpen,
    library.close,
    learning.close,
    library.ref,
    learning.ref,
  ]);

  const onLibraryKeyDown = (e: ReactKeyboardEvent<HTMLButtonElement>) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      library.toggle();
      return;
    }
    if (e.key === "ArrowDown") {
      e.preventDefault();
      library.setOpen(true);
      requestAnimationFrame(() => {
        const first = library.ref.current?.querySelector<HTMLElement>(
          "[data-library-category]",
        );
        first?.focus();
      });
    }
  };

  const onLearningKeyDown = (e: ReactKeyboardEvent<HTMLButtonElement>) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      learning.toggle();
    }
  };

  const panelItems =
    libraryCategory === "books"
      ? LIBRARY_MENU_BOOKS
      : libraryCategory === "practice"
        ? LIBRARY_MENU_PRACTICE
        : libraryCategory === "educator"
          ? LIBRARY_MENU_EDUCATOR
          : null;

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
          aria-expanded={mobileOpen}
          aria-controls="primary-nav"
          onClick={() => setMobileOpen((v) => !v)}
        >
          Menu
        </button>

        <nav
          id="primary-nav"
          className={`nav ${mobileOpen ? "nav--open" : ""}`}
          aria-label="Primary navigation"
        >
          {primary.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              aria-current={isActive(pathname, item.href) ? "page" : undefined}
            >
              {item.label}
            </Link>
          ))}

          {/* Desktop Library two-panel menu */}
          <div
            className="nav-dropdown nav-library nav-library--desktop"
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
              onKeyDown={onLibraryKeyDown}
            >
              Library
            </button>
            <div
              id={libraryId}
              className="nav-dropdown__menu nav-library__menu nav-library__menu--two-panel"
              data-state={library.open ? "open" : "closed"}
              role="group"
              aria-label="Library categories"
            >
              <div className="nav-library-panel nav-library-panel--categories" role="presentation">
                {LIBRARY_CATEGORIES.map((cat) =>
                  cat.id === "home" ? (
                    <Link
                      key={cat.id}
                      href="/library"
                      className="nav-library-category"
                      data-library-category=""
                      aria-current={pathname === "/library" ? "page" : undefined}
                      onClick={() => library.close(false)}
                      onFocus={() => setLibraryCategory("home")}
                      onMouseEnter={() => setLibraryCategory("home")}
                    >
                      {cat.label}
                    </Link>
                  ) : (
                    <button
                      key={cat.id}
                      type="button"
                      className="nav-library-category"
                      data-library-category=""
                      data-active={libraryCategory === cat.id ? "true" : "false"}
                      aria-controls={categoryPanelId}
                      aria-pressed={libraryCategory === cat.id}
                      onMouseEnter={() => setLibraryCategory(cat.id)}
                      onFocus={() => setLibraryCategory(cat.id)}
                      onClick={() => setLibraryCategory(cat.id)}
                    >
                      {cat.label}
                    </button>
                  ),
                )}
              </div>
              <div
                id={categoryPanelId}
                className="nav-library-panel nav-library-panel--items"
                role="group"
                aria-label={
                  LIBRARY_CATEGORIES.find((c) => c.id === libraryCategory)
                    ?.label ?? "Library links"
                }
              >
                {libraryCategory === "home" ? (
                  <Link
                    href="/library"
                    onClick={() => library.close(false)}
                    aria-current={pathname === "/library" ? "page" : undefined}
                  >
                    Browse all collections
                  </Link>
                ) : panelItems ? (
                  <MenuLinks
                    items={panelItems}
                    pathname={pathname}
                    onNavigate={() => library.close(false)}
                  />
                ) : null}
              </div>
            </div>
          </div>

          {/* Mobile Library accordion */}
          <div className="nav-accordion nav-library--mobile">
            <button
              type="button"
              className="nav-accordion__button"
              aria-expanded={mobileLibraryOpen}
              aria-controls={`${libraryId}-mobile`}
              onClick={() => setMobileLibraryOpen((v) => !v)}
            >
              Library
            </button>
            <div
              id={`${libraryId}-mobile`}
              className="nav-accordion__panel"
              hidden={!mobileLibraryOpen}
            >
              <Link href="/library" className="nav-mega-home">
                Library Home
              </Link>
              {LIBRARY_CATEGORIES.filter((c) => c.id !== "home").map((cat) => {
                const open = mobileLibraryPanel === cat.id;
                const items =
                  cat.id === "books"
                    ? LIBRARY_MENU_BOOKS
                    : cat.id === "practice"
                      ? LIBRARY_MENU_PRACTICE
                      : LIBRARY_MENU_EDUCATOR;
                return (
                  <div key={cat.id} className="nav-accordion-sub">
                    <button
                      type="button"
                      className="nav-accordion-sub__button"
                      aria-expanded={open}
                      aria-controls={`${libraryId}-${cat.id}`}
                      onClick={() =>
                        setMobileLibraryPanel((prev) =>
                          prev === cat.id ? null : cat.id,
                        )
                      }
                    >
                      {cat.label}
                    </button>
                    <div
                      id={`${libraryId}-${cat.id}`}
                      className="nav-accordion-sub__panel"
                      hidden={!open}
                    >
                      <MenuLinks
                        items={items}
                        pathname={pathname}
                        onNavigate={() => setMobileOpen(false)}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Learning desktop */}
          <div
            className="nav-dropdown nav-learning nav-learning--desktop"
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
              onKeyDown={onLearningKeyDown}
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

          {/* Learning mobile accordion */}
          <div className="nav-accordion nav-learning--mobile">
            <button
              type="button"
              className="nav-accordion__button"
              aria-expanded={mobileLearningOpen}
              aria-controls={`${learningId}-mobile`}
              aria-haspopup="true"
              onClick={() => setMobileLearningOpen((v) => !v)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  setMobileLearningOpen((v) => !v);
                }
              }}
            >
              Learning
            </button>
            <div
              id={`${learningId}-mobile`}
              className="nav-accordion__panel nav-learning__menu"
              role="group"
              aria-label="Learning links"
              hidden={!mobileLearningOpen}
              data-state={mobileLearningOpen ? "open" : "closed"}
            >
              {learningLinks.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-current={isActive(pathname, item.href) ? "page" : undefined}
                  onClick={() => {
                    setMobileLearningOpen(false);
                    setMobileOpen(false);
                  }}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>

          {trailing.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              aria-current={isActive(pathname, item.href) ? "page" : undefined}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
