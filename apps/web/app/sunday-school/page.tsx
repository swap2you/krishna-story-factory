"use client";

import { useState } from "react";
import { PageIntro } from "@/components/page-intro";

type AgeGroup = "bal-gopal" | "damodara" | "mixed";

const AGE_GROUPS: { id: AgeGroup; label: string; ages: string; desc: string }[] = [
  { id: "bal-gopal", label: "Bal Gopal", ages: "Ages 5–8", desc: "Shorter stories, simple coloring, gentle activities, lots of singing and movement." },
  { id: "damodara", label: "Dāmodara", ages: "Ages 9–13", desc: "Full narrations, deeper discussion, detailed coloring, written activities and śloka memorization." },
  { id: "mixed", label: "Mixed age", ages: "All ages", desc: "Layered approach — simple tasks for younger, extension prompts for older. Buddy pairing encouraged." },
];

const WEEKLY_PLAN = [
  { step: "Opening", time: "5 min", detail: "Maṅgalācaraṇa prayers and attendance. Light a lamp if possible." },
  { step: "Story time", time: "10–15 min", detail: "Read or play audio narration from the week's story package." },
  { step: "Discussion", time: "5–10 min", detail: "Age-appropriate questions. Bal Gopal: recall. Dāmodara: reflection and meaning." },
  { step: "Activity", time: "10–15 min", detail: "Coloring pages, activity sheets, or śloka practice cards." },
  { step: "Closing", time: "5 min", detail: "Recap, homework assignment, and closing prayers." },
];

const HOMEWORK_CHECKLIST = [
  "Listen to the story narration at least once at home.",
  "Complete the coloring page (simple or detailed as appropriate).",
  "Practice the week's śloka or prayer with a family member.",
  "Share one thing you learned with a parent or sibling.",
  "Bring your completed activity sheet to the next class.",
];

const FESTIVAL_UNITS = [
  { name: "Janmāṣṭamī", desc: "Multi-week unit on Lord Kṛṣṇa's appearance, Mathurā pastimes, and Nanda Mahārāja's celebrations." },
  { name: "Gaura Pūrṇimā", desc: "The appearance of Śrī Caitanya Mahāprabhu, Navadvīpa pastimes, and the saṅkīrtana movement." },
  { name: "Rāma Navamī", desc: "Lord Rāma's appearance, Ayodhyā, and the values of dharma and devotion." },
  { name: "Govardhana Pūjā", desc: "The lifting of Govardhana Hill — themes of surrender, protection, and community." },
  { name: "Ratha-yātrā", desc: "Lord Jagannātha's chariot festival — history, mood, and how families can participate." },
];

const PARENT_MESSAGE = `Dear Parent / Guardian,

Thank you for supporting your child's participation in Sunday School. This week we explored a new story from our devotional collection.

Please encourage your child to:
• Listen to the audio narration at home
• Complete the coloring and activity pages
• Practice the śloka or prayer of the week

If you have questions or feedback, please speak with the class teacher. We value your partnership in your child's devotional education.

With warm regards,
The Sunday School Team`;

export default function SundaySchoolPage() {
  const [selectedGroup, setSelectedGroup] = useState<AgeGroup>("mixed");

  return (
    <>
      <PageIntro
        eyebrow="Sunday School"
        title="Structured devotional classes for every age."
        body="Weekly plans, homework checklists, parent message templates, and festival-unit cards — everything a Sunday school teacher needs to create a calm, engaging classroom."
      />
      <section className="section">
        <div className="container" style={{ maxWidth: 960 }}>
          <section className="teacher-panel">
            <h2>Age groups</h2>
            <p className="hint">Select an age group to see tailored guidance. All groups use the same story packages with different depth.</p>
            <div className="mode-grid">
              {AGE_GROUPS.map((g) => (
                <button
                  key={g.id}
                  type="button"
                  className={`mode-card${selectedGroup === g.id ? " is-active" : ""}`}
                  onClick={() => setSelectedGroup(g.id)}
                >
                  <strong>{g.label}</strong>
                  <span>{g.ages}</span>
                </button>
              ))}
            </div>
            <div className="source-boundary">
              <strong>{AGE_GROUPS.find((g) => g.id === selectedGroup)?.label}</strong>
              <p style={{ margin: ".35rem 0 0" }}>{AGE_GROUPS.find((g) => g.id === selectedGroup)?.desc}</p>
            </div>
          </section>

          <section className="teacher-panel" style={{ marginTop: "1.25rem" }}>
            <h2>Weekly class plan</h2>
            <p className="hint">A suggested 35–50 minute structure. Adjust timings to fit your community.</p>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", marginTop: ".75rem" }}>
                <thead>
                  <tr style={{ borderBottom: "2px solid var(--bhava-border)" }}>
                    <th style={{ textAlign: "left", padding: ".65rem .5rem", fontSize: ".82rem", textTransform: "uppercase", letterSpacing: ".06em", color: "var(--bhava-saffron)", fontWeight: 800 }}>Step</th>
                    <th style={{ textAlign: "left", padding: ".65rem .5rem", fontSize: ".82rem", textTransform: "uppercase", letterSpacing: ".06em", color: "var(--bhava-saffron)", fontWeight: 800 }}>Time</th>
                    <th style={{ textAlign: "left", padding: ".65rem .5rem", fontSize: ".82rem", textTransform: "uppercase", letterSpacing: ".06em", color: "var(--bhava-saffron)", fontWeight: 800 }}>Detail</th>
                  </tr>
                </thead>
                <tbody>
                  {WEEKLY_PLAN.map((row) => (
                    <tr key={row.step} style={{ borderBottom: "1px solid rgba(20,40,70,.06)" }}>
                      <td style={{ padding: ".65rem .5rem", fontWeight: 700, color: "var(--bhava-midnight)" }}>{row.step}</td>
                      <td style={{ padding: ".65rem .5rem", whiteSpace: "nowrap", color: "var(--bhava-muted)" }}>{row.time}</td>
                      <td style={{ padding: ".65rem .5rem", color: "var(--bhava-muted)", lineHeight: 1.5 }}>{row.detail}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="teacher-panel" style={{ marginTop: "1.25rem" }}>
            <h2>Homework checklist</h2>
            <p className="hint">Print and distribute to families. Children check off items during the week.</p>
            <ul className="checklist">
              {HOMEWORK_CHECKLIST.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </section>

          <section className="teacher-panel" style={{ marginTop: "1.25rem" }}>
            <h2>Parent message template</h2>
            <p className="hint">Copy and customize for your weekly parent communication.</p>
            <pre style={{ whiteSpace: "pre-wrap", padding: "1rem", borderRadius: ".9rem", background: "rgba(255,250,242,.8)", border: "1px solid var(--bhava-border)", fontFamily: "var(--font-body), sans-serif", fontSize: ".92rem", lineHeight: 1.65, color: "var(--bhava-ink)" }}>
              {PARENT_MESSAGE}
            </pre>
          </section>

          <section className="teacher-panel" style={{ marginTop: "1.25rem" }}>
            <h2>Festival-unit cards</h2>
            <p className="hint">Multi-week themed units tied to the Vaiṣṇava calendar. Each unit will connect stories, activities, and celebrations.</p>
            <div className="sunday-grid">
              {FESTIVAL_UNITS.map((f) => (
                <article key={f.name} className="sunday-card">
                  <h3>{f.name}</h3>
                  <p className="hint">{f.desc}</p>
                  <span className="editorial-status planned" style={{ marginTop: ".75rem" }}>Planned</span>
                </article>
              ))}
            </div>
          </section>
        </div>
      </section>
    </>
  );
}
