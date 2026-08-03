import { describe, expect, it } from "vitest";

type Verse = Record<string, unknown>;

/** Pure helper mirroring Ślokas tab presentation rules (D-01). */
export function presentShloka(verse: Verse) {
  const reviewStatus = String(verse.review_status ?? "");
  const notApplicable =
    reviewStatus === "not_applicable" || String(verse.decision ?? "") === "no-separate-verse";
  const reference = String(verse.reference ?? "").trim();
  const explanation = String(verse.child_explanation ?? "").trim();
  const url = typeof verse.url === "string" ? verse.url.trim() : "";
  const sanskrit = String(verse.sanskrit ?? verse.devanagari ?? "").trim();
  const transliteration = String(verse.transliteration ?? "").trim();
  const translation = String(verse.translation ?? "").trim();
  const stateLabel = notApplicable
    ? "No separate verse selected"
    : reviewStatus === "reviewed"
      ? "Reviewed companion reference"
      : "Companion reference";
  const chapterReferenceBadge =
    !notApplicable && (!reference || !/\d+\.\d+\.\d+/.test(reference) || reviewStatus !== "reviewed");
  return {
    stateLabel,
    notApplicable,
    reference,
    explanation,
    url,
    vedabaseLabel: url ? "Read this passage on Vedabase" : "",
    chapterReferenceBadge,
    showSanskrit: Boolean(sanskrit),
    showTransliteration: Boolean(transliteration),
    showTranslation: Boolean(translation),
    emDashFiller: false,
  };
}

describe("Śloka panel presentation (D-01)", () => {
  it("renders ordinary reviewed chapter/range reference with child explanation and Vedabase link", () => {
    const view = presentShloka({
      reference: "SB 10.7 (Tṛṇāvarta whirlwind pastime)",
      url: "https://vedabase.io/en/library/sb/10/7/",
      child_explanation: "Baby Kṛṣṇa is carried by the whirlwind demon and remains protected.",
      review_status: "reviewed",
      sanskrit: null,
      transliteration: null,
    });
    expect(view.stateLabel).toBe("Reviewed companion reference");
    expect(view.reference).toContain("SB 10.7");
    expect(view.explanation).toMatch(/whirlwind/i);
    expect(view.url).toContain("vedabase.io");
    expect(view.vedabaseLabel).toBe("Read this passage on Vedabase");
    expect(view.chapterReferenceBadge).toBe(true);
    expect(view.showSanskrit).toBe(false);
    expect(view.emDashFiller).toBe(false);
  });

  it("exact verse references do not show Chapter reference badge when reviewed", () => {
    const view = presentShloka({
      reference: "SB 10.12.1–10.12.44",
      url: "https://vedabase.io/en/library/sb/10/12/",
      review_status: "reviewed",
      child_explanation: "Aghāsura pastime.",
    });
    expect(view.chapterReferenceBadge).toBe(false);
  });

  it("presents not_applicable honestly and never as REVIEWED", () => {
    const view = presentShloka({
      reference: "No separate verse selected for this bedtime adaptation",
      child_explanation: "Open the Source tab for the Krishna Book chapter study link.",
      review_status: "not_applicable",
      decision: "no-separate-verse",
      sanskrit: null,
    });
    expect(view.notApplicable).toBe(true);
    expect(view.stateLabel).toBe("No separate verse selected");
    expect(view.stateLabel.toLowerCase()).not.toContain("reviewed companion");
  });

  it("missing Sanskrit does not invent em-dash content fields", () => {
    const view = presentShloka({
      reference: "SB 10.11",
      child_explanation: "Kṛṣṇa protects the calves.",
      review_status: "reviewed",
      sanskrit: null,
      transliteration: null,
      translation: null,
    });
    expect(view.showSanskrit).toBe(false);
    expect(view.showTransliteration).toBe(false);
    expect(view.showTranslation).toBe(false);
  });

  it("covers Stories 001, 005, 006, 011, 019, 020 status patterns", () => {
    const cases: Array<[string, Verse]> = [
      ["001", { review_status: "not_applicable", decision: "no-separate-verse", reference: "No separate verse selected for this bedtime adaptation", child_explanation: "Earth's prayer framing." }],
      ["005", { review_status: "not_applicable", decision: "no-separate-verse", reference: "No separate verse selected for this bedtime adaptation", child_explanation: "Demigod prayers framing." }],
      ["006", { review_status: "not_applicable", decision: "no-separate-verse", reference: "No separate verse selected for this bedtime adaptation", child_explanation: "Birth pastime framing." }],
      ["011", { review_status: "reviewed", reference: "SB 10.7", url: "https://vedabase.io/en/library/sb/10/7/", child_explanation: "Tṛṇāvarta." }],
      ["019", { review_status: "reviewed", reference: "SB 10.11", url: "https://vedabase.io/en/library/sb/10/11/", child_explanation: "Vatsāsura and Bakāsura." }],
      ["020", { review_status: "reviewed", reference: "SB 10.12", url: "https://vedabase.io/en/library/sb/10/12/", child_explanation: "Aghāsura." }],
    ];
    for (const [story, verse] of cases) {
      const view = presentShloka(verse);
      expect(view.reference.length, story).toBeGreaterThan(3);
      expect(view.explanation.length, story).toBeGreaterThan(3);
      if (story === "001" || story === "005" || story === "006") {
        expect(view.notApplicable, story).toBe(true);
      } else {
        expect(view.url, story).toContain("vedabase.io");
      }
    }
  });
});
