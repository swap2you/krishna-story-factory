import { describe, expect, it } from "vitest";
import {
  isLoopbackHostName,
  isLoopbackRequest,
  parseHostName,
} from "@/lib/knowledge/studio-guard";

describe("parseHostName", () => {
  it("parses ipv4 with port", () => {
    expect(parseHostName("127.0.0.1:3000")).toBe("127.0.0.1");
  });
  it("parses localhost with port", () => {
    expect(parseHostName("localhost:3017")).toBe("localhost");
  });
  it("parses bracketed ipv6 with port", () => {
    expect(parseHostName("[::1]:3000")).toBe("::1");
  });
  it("parses bare ipv6", () => {
    expect(parseHostName("::1")).toBe("::1");
  });
  it("parses ipv4-mapped ipv6", () => {
    expect(parseHostName("[::ffff:127.0.0.1]:443")).toBe("::ffff:127.0.0.1");
  });
});

describe("isLoopbackHostName", () => {
  it("accepts loopback positives", () => {
    for (const h of [
      "localhost",
      "127.0.0.1",
      "127.1.2.3",
      "::1",
      "[::1]",
      "::ffff:127.0.0.1",
      "::ffff:127.10.0.1",
    ]) {
      expect(isLoopbackHostName(h), h).toBe(true);
    }
  });
  it("rejects non-loopback negatives", () => {
    for (const h of [
      "",
      "example.com",
      "192.168.1.1",
      "10.0.0.1",
      "8.8.8.8",
      "::ffff:8.8.8.8",
      "bhava.local",
    ]) {
      expect(isLoopbackHostName(h), h).toBe(false);
    }
  });
});

describe("isLoopbackRequest", () => {
  it("accepts localhost host without forwarded headers", () => {
    expect(isLoopbackRequest(new Headers({ host: "localhost:3017" }))).toBe(true);
  });
  it("accepts [::1]:port", () => {
    expect(isLoopbackRequest(new Headers({ host: "[::1]:3017" }))).toBe(true);
  });
  it("accepts loopback x-forwarded-for hops", () => {
    expect(
      isLoopbackRequest(
        new Headers({
          host: "127.0.0.1:3017",
          "x-forwarded-for": "127.0.0.1",
        }),
      ),
    ).toBe(true);
  });
  it("rejects public host", () => {
    expect(isLoopbackRequest(new Headers({ host: "example.com" }))).toBe(false);
  });
  it("rejects public x-forwarded-for even with localhost host", () => {
    expect(
      isLoopbackRequest(
        new Headers({
          host: "localhost",
          "x-forwarded-for": "8.8.8.8",
        }),
      ),
    ).toBe(false);
  });
  it("rejects public x-forwarded-host", () => {
    expect(
      isLoopbackRequest(
        new Headers({
          host: "127.0.0.1",
          "x-forwarded-host": "evil.example",
        }),
      ),
    ).toBe(false);
  });
});
