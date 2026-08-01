/**
 * Nested-safe body scroll lock for overlays / drawers.
 * Only the first lock applies styles; unlock restores when the count hits 0.
 */

let lockCount = 0;
let savedScrollY = 0;
let savedBodyCssText = "";
let savedHtmlScrollBehavior = "";

export function lockBodyScroll(): { unlock: () => void } {
  if (typeof window === "undefined") {
    return { unlock: () => undefined };
  }

  lockCount += 1;

  if (lockCount === 1) {
    savedScrollY = window.scrollY || window.pageYOffset || document.documentElement.scrollTop || 0;
    savedBodyCssText = document.body.style.cssText;
    savedHtmlScrollBehavior = document.documentElement.style.scrollBehavior;

    const scrollbarWidth =
      window.innerWidth - document.documentElement.clientWidth;

    // Avoid smooth-scroll interference while locking/unlocking (see globals.css).
    document.documentElement.style.scrollBehavior = "auto";

    document.body.style.position = "fixed";
    document.body.style.top = `-${savedScrollY}px`;
    document.body.style.left = "0";
    document.body.style.right = "0";
    document.body.style.width = "100%";
    if (scrollbarWidth > 0) {
      document.body.style.paddingRight = `${scrollbarWidth}px`;
    }
  }

  let unlocked = false;

  return {
    unlock: () => {
      if (unlocked) return;
      unlocked = true;

      if (typeof window === "undefined") return;

      lockCount = Math.max(0, lockCount - 1);
      if (lockCount !== 0) return;

      document.body.style.cssText = savedBodyCssText;
      // Force layout before restoring scroll (esp. mobile Chromium).
      void document.body.offsetHeight;
      window.scrollTo(0, savedScrollY);
      document.documentElement.scrollTop = savedScrollY;
      document.body.scrollTop = savedScrollY;
      document.documentElement.style.scrollBehavior = savedHtmlScrollBehavior;
    },
  };
}

/** Test-only: reset nested lock counter and saved state. */
export function __resetBodyScrollLockForTests(): void {
  lockCount = 0;
  savedScrollY = 0;
  savedBodyCssText = "";
  savedHtmlScrollBehavior = "";
  if (typeof window !== "undefined" && typeof document !== "undefined") {
    document.body.style.cssText = "";
    document.documentElement.style.scrollBehavior = "";
  }
}
