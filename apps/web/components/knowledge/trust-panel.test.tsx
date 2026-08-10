import { describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { TrustPanel } from "./trust-panel";

describe("TrustPanel", () => {
  it("supports uncontrolled defaultOpen without locking open prop", () => {
    const html = renderToStaticMarkup(
      <TrustPanel rows={[{ label: "Review", value: "approved" }]} defaultOpen />,
    );
    expect(html).toContain("Source and review");
    expect(html).toContain("open");
  });
});
