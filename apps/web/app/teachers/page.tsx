"use client";

import { useMemo, useState } from "react";
import { Button } from "@bhava/ui";
import { PageIntro } from "@/components/page-intro";

type AgeMode = "bal-gopal" | "damodara" | "mixed";

const PACK_OPTIONS = [
  { id: "story", label: "Story reading", tip: "Shared reading time" },
  { id: "audio", label: "Audio listening", tip: "Narration circle" },
  { id: "coloring", label: "Coloring pages", tip: "Quiet hands" },
  { id: "activity", label: "Activity sheet", tip: "Guided worksheet" },
  { id: "shloka", label: "Śloka card", tip: "When curated" },
];

export default function TeachersPage() {
  const [mode, setMode] = useState<AgeMode>("mixed");
  const [selected, setSelected] = useState<string[]>(["story", "audio", "coloring"]);
  const [minutes, setMinutes] = useState(30);
  const [showAnswers, setShowAnswers] = useState(false);

  const guidance = useMemo(() => {
    if (mode === "bal-gopal") {
      return "Ages ~5–8: shorter listen, simple coloring, one gentle activity. Keep answer keys for adults only.";
    }
    if (mode === "damodara") {
      return "Ages ~9–13: full narration, detailed coloring, activity with discussion prompts.";
    }
    return "Mixed class: offer both simple and detailed paths; let children choose coloring depth.";
  }, [mode]);

  return (
    <>
      <PageIntro
        eyebrow="For teachers"
        title="Age-aware class packs with calm clarity."
        body="Compose a printable plan for Bal Gopal, Dāmodara, or mixed-age groups. Answer keys stay separated from the child view."
      />
      <section className="section">
        <div className="container teacher-stack">
          <section className="teacher-panel">
            <h2>1 · Choose an age mode</h2>
            <div className="mode-grid">
              {([
                ["bal-gopal", "Bal Gopal", "Younger children"],
                ["damodara", "Dāmodara", "Older children"],
                ["mixed", "Mixed age", "Whole class"],
              ] as const).map(([value, label, tip]) => (
                <button
                  key={value}
                  type="button"
                  className={`mode-card${mode === value ? " is-active" : ""}`}
                  onClick={() => setMode(value)}
                >
                  <strong>{label}</strong>
                  <span>{tip}</span>
                </button>
              ))}
            </div>
            <p className="hint">{guidance}</p>
            <label style={{ display: "inline-flex", gap: ".75rem", alignItems: "center", marginTop: "1rem" }}>
              Lesson timing (minutes)
              <input
                type="number"
                min={10}
                max={90}
                value={minutes}
                onChange={(event) => setMinutes(Number(event.target.value))}
                style={{ minHeight: 44, width: 88, borderRadius: 12, border: "1px solid var(--bhava-border)", padding: "0 .6rem" }}
              />
            </label>
          </section>

          <section className="teacher-panel">
            <h2>2 · Compose the class pack</h2>
            <p className="hint">Tap cards to include them. Selected items become your printable plan.</p>
            <div className="pack-grid">
              {PACK_OPTIONS.map((option) => {
                const on = selected.includes(option.id);
                return (
                  <button
                    key={option.id}
                    type="button"
                    className={`pack-option${on ? " is-on" : ""}`}
                    onClick={() =>
                      setSelected((current) =>
                        on ? current.filter((id) => id !== option.id) : [...current, option.id],
                      )
                    }
                  >
                    {option.label}
                    <span style={{ display: "block", marginTop: ".35rem", fontWeight: 500, color: "var(--bhava-muted)", fontSize: ".85rem" }}>
                      {option.tip}
                    </span>
                  </button>
                );
              })}
            </div>
            <p><strong>Selected:</strong> {selected.join(", ") || "none yet"}</p>
            <div className="actions" style={{ marginTop: "1rem" }}>
              <Button
                onClick={() => {
                  const plan = `Bhāva class pack\nSteward: Svarna Gauranga Das\nMode: ${mode}\nMinutes: ${minutes}\nItems: ${selected.join(", ")}\n`;
                  localStorage.setItem("bhava:class-pack", plan);
                  window.print();
                }}
              >
                Print / export preview
              </Button>
              <Button
                variant="quiet"
                onClick={() => {
                  const existing = JSON.parse(localStorage.getItem("bhava:classroom-playlist") || "[]");
                  existing.push({ mode, minutes, selected, at: new Date().toISOString() });
                  localStorage.setItem("bhava:classroom-playlist", JSON.stringify(existing));
                }}
              >
                Save to classroom playlist
              </Button>
            </div>
          </section>

          <section className="teacher-panel">
            <h2>3 · Answer key (adults only)</h2>
            <p className="hint">Child-facing activity pages never show this block by default.</p>
            <Button variant="quiet" onClick={() => setShowAnswers((value) => !value)}>
              {showAnswers ? "Hide answer key" : "Reveal answer key"}
            </Button>
            {showAnswers ? (
              <div className="source-boundary" style={{ marginTop: "1rem" }}>
                Use the package <code>manifest.json</code> parent answer key when present. Do not invent answers for missing keys.
              </div>
            ) : null}
          </section>
        </div>
      </section>
    </>
  );
}
