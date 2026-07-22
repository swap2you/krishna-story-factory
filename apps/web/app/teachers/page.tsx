"use client";

import { useMemo, useState } from "react";
import { Button, Card } from "@bhava/ui";
import { PageIntro } from "@/components/page-intro";

type AgeMode = "bal-gopal" | "damodara" | "mixed";

const PACK_OPTIONS = [
  { id: "story", label: "Story reading" },
  { id: "audio", label: "Audio listening" },
  { id: "coloring", label: "Coloring pages" },
  { id: "activity", label: "Activity sheet" },
  { id: "shloka", label: "Śloka card (when curated)" },
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
        title="Age-aware class packs without cloud child accounts."
        body="Compose a printable plan for Bal Gopal, Dāmodara, or mixed-age groups. Answer keys stay separated from the child view."
      />
      <section className="section">
        <div className="container" style={{ display: "grid", gap: "1.25rem" }}>
          <Card className="story-content">
            <h2>Age mode</h2>
            <div className="actions">
              {([
                ["bal-gopal", "Bal Gopal"],
                ["damodara", "Dāmodara"],
                ["mixed", "Mixed age"],
              ] as const).map(([value, label]) => (
                <Button key={value} variant={mode === value ? "accent" : "quiet"} onClick={() => setMode(value)}>
                  {label}
                </Button>
              ))}
            </div>
            <p>{guidance}</p>
            <label>
              Lesson timing (minutes)
              <input
                type="number"
                min={10}
                max={90}
                value={minutes}
                onChange={(event) => setMinutes(Number(event.target.value))}
                style={{ marginLeft: "0.75rem", minHeight: 44 }}
              />
            </label>
          </Card>

          <Card className="story-content">
            <h2>Class-pack composer</h2>
            <div className="actions">
              {PACK_OPTIONS.map((option) => {
                const on = selected.includes(option.id);
                return (
                  <Button
                    key={option.id}
                    variant={on ? "primary" : "quiet"}
                    onClick={() =>
                      setSelected((current) =>
                        on ? current.filter((id) => id !== option.id) : [...current, option.id],
                      )
                    }
                  >
                    {option.label}
                  </Button>
                );
              })}
            </div>
            <p>Selected: {selected.join(", ") || "none"}</p>
            <div className="actions">
              <Button
                onClick={() => {
                  const plan = `Bhāva class pack\nMode: ${mode}\nMinutes: ${minutes}\nItems: ${selected.join(", ")}\n`;
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
          </Card>

          <Card className="story-content">
            <h2>Answer key (adults / teachers)</h2>
            <p>Child-facing activity pages never show this block by default.</p>
            <Button variant="quiet" onClick={() => setShowAnswers((value) => !value)}>
              {showAnswers ? "Hide answer key" : "Reveal answer key"}
            </Button>
            {showAnswers ? (
              <p>
                Use the package <code>manifest.json</code> activity parent answer key when present. Do not invent answers
                for missing keys.
              </p>
            ) : null}
          </Card>
        </div>
      </section>
    </>
  );
}
