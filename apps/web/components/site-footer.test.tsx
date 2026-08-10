import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("@/lib/release-meta", () => ({
  getBhavaReleaseMeta: () => ({
    webVersion: "001-020-v4",
    contentRelease: "bhava-content-001-020-v4",
    shortSha: "abc1234",
  }),
}));

describe("SiteFooter version Env", () => {
  afterEach(() => {
    vi.resetModules();
    delete process.env.BHAVA_ENVIRONMENT;
    delete process.env.NEXT_PUBLIC_BHAVA_ENV;
  });

  it("prefers BHAVA_ENVIRONMENT over NEXT_PUBLIC_BHAVA_ENV and NODE_ENV", async () => {
    process.env.BHAVA_ENVIRONMENT = "staging";
    process.env.NEXT_PUBLIC_BHAVA_ENV = "ignored";
    const { SiteFooter } = await import("./site-footer");
    render(<SiteFooter />);
    expect(screen.getByText("staging")).toBeInTheDocument();
  });

  it("renders approved Bhāva/Dauji footer without civil name", async () => {
    const { SiteFooter } = await import("./site-footer");
    const { container } = render(<SiteFooter />);
    expect(container.textContent).toMatch(/Svarna Gauranga Das · Dauji Publication · Bhāva/);
    expect(container.textContent).not.toMatch(/Swapnil Patil/);
  });
});
