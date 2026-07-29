"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import contact from "@/config/contact.json";
import { PageIntro } from "@/components/page-intro";
import { buildContactMailto } from "@/lib/email-adapter";

export default function KnowledgeAskPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [errors, setErrors] = useState<string[]>([]);
  const [copied, setCopied] = useState(false);
  const pageUrl = useMemo(
    () => (typeof window !== "undefined" ? window.location.href : "https://bhava.local/knowledge/ask"),
    [],
  );

  function validate() {
    const next: string[] = [];
    if (!name.trim()) next.push("Name is required.");
    if (!email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) next.push("Valid email required.");
    if (!subject.trim()) next.push("Subject is required.");
    if (message.trim().length < 10) next.push("Question must be at least 10 characters.");
    return next;
  }

  const mailto = buildContactMailto(
    {
      name: name.trim(),
      email: email.trim(),
      topic: "Devotional/source question",
      subject: `[Knowledge question] ${subject.trim()}`,
      message: message.trim(),
      pageUrl,
    },
    contact.public_email,
  );

  return (
    <>
      <PageIntro
        eyebrow="Private question"
        title="Ask the steward"
        body="Questions are private. Nothing is stored on Bhāva servers. Your email app opens a prepared message — we never show a false “sent” state."
      />
      <section className="section">
        <div className="container" style={{ maxWidth: 640 }}>
          <form
            className="contact-form"
            onSubmit={(e) => {
              e.preventDefault();
              const next = validate();
              setErrors(next);
              if (!next.length) window.location.href = mailto;
            }}
          >
            <label>Name<input value={name} onChange={(e) => setName(e.target.value)} /></label>
            <label>Email<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} /></label>
            <label>Subject<input value={subject} onChange={(e) => setSubject(e.target.value)} /></label>
            <label>Question<textarea rows={6} value={message} onChange={(e) => setMessage(e.target.value)} /></label>
            {errors.length ? (
              <ul role="alert">{errors.map((err) => <li key={err}>{err}</li>)}</ul>
            ) : null}
            <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
              <a className="bhava-button bhava-button--primary" href={mailto} onClick={() => setErrors(validate())}>
                Open in email app
              </a>
              <button
                type="button"
                className="bhava-button bhava-button--quiet"
                onClick={async () => {
                  const next = validate();
                  setErrors(next);
                  if (next.length) return;
                  await navigator.clipboard.writeText(
                    `To: ${contact.public_email}\nSubject: [Knowledge question] ${subject}\n\n${message}`,
                  );
                  setCopied(true);
                }}
              >
                {copied ? "Copied" : "Copy message"}
              </button>
            </div>
          </form>
          <p className="hint" style={{ marginTop: "1rem" }}>
            Do not include sensitive information about children. <Link href="/knowledge">← Knowledge</Link>
          </p>
        </div>
      </section>
    </>
  );
}
