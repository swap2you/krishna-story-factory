import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  __resetBodyScrollLockForTests,
  lockBodyScroll,
} from "./body-scroll-lock";

describe("lockBodyScroll", () => {
  beforeEach(() => {
    __resetBodyScrollLockForTests();
    vi.spyOn(window, "scrollTo").mockImplementation(() => undefined);
    Object.defineProperty(window, "scrollY", {
      configurable: true,
      get: () => 240,
    });
    Object.defineProperty(window, "innerWidth", {
      configurable: true,
      value: 1024,
    });
    Object.defineProperty(document.documentElement, "clientWidth", {
      configurable: true,
      value: 1008,
    });
  });

  afterEach(() => {
    __resetBodyScrollLockForTests();
    vi.restoreAllMocks();
  });

  it("locks body with fixed position and compensates scrollbar width", () => {
    const { unlock } = lockBodyScroll();

    expect(document.body.style.position).toBe("fixed");
    expect(document.body.style.top).toBe("-240px");
    expect(document.body.style.width).toBe("100%");
    expect(document.body.style.paddingRight).toBe("16px");

    unlock();

    expect(document.body.style.position).toBe("");
    expect(document.body.style.top).toBe("");
    expect(document.body.style.paddingRight).toBe("");
    expect(window.scrollTo).toHaveBeenCalledWith(0, 240);
  });

  it("supports nested locks: styles apply once and restore on final unlock", () => {
    const first = lockBodyScroll();
    expect(document.body.style.position).toBe("fixed");

    const second = lockBodyScroll();
    // Nested lock must not re-apply / wipe styles
    expect(document.body.style.position).toBe("fixed");
    expect(document.body.style.top).toBe("-240px");

    first.unlock();
    expect(document.body.style.position).toBe("fixed");
    expect(window.scrollTo).not.toHaveBeenCalled();

    second.unlock();
    expect(document.body.style.position).toBe("");
    expect(window.scrollTo).toHaveBeenCalledWith(0, 240);
  });

  it("ignores duplicate unlock calls on the same handle", () => {
    const a = lockBodyScroll();
    const b = lockBodyScroll();

    a.unlock();
    a.unlock(); // should not decrement past the nested pair incorrectly
    expect(document.body.style.position).toBe("fixed");

    b.unlock();
    expect(document.body.style.position).toBe("");
    expect(window.scrollTo).toHaveBeenCalledTimes(1);
  });

  it("skips paddingRight when scrollbar width is 0", () => {
    Object.defineProperty(window, "innerWidth", {
      configurable: true,
      value: 1000,
    });
    Object.defineProperty(document.documentElement, "clientWidth", {
      configurable: true,
      value: 1000,
    });

    const { unlock } = lockBodyScroll();
    expect(document.body.style.paddingRight).toBe("");
    unlock();
  });
});
