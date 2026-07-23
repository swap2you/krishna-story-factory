"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import contact from "@/config/contact.json";
import { PageIntro } from "@/components/page-intro";
import { buildContactMailto } from "@/lib/email-adapter";

const TOPICS = [
  "Content correction",
  "Devotional/source question",
  "Teacher feedback",
  "Technical issue",
  "Suggestion",
  "Other",
] as const;

export default function ContactPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [topic, setTopic] = useState<(typeof TOPICS)[number]>("Suggestion");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [errors, setErrors] = useState<string[]>([]);
  const [copied, setCopied] = useState(false);

  const pageUrl = useMemo(() => (typeof window !== "undefined" ? window.location.href : "https://bhava.local/contact"), []);

  function validate(): string[] {
    const next: string[] = [];
    if (!name.trim()) next.push("Name is required.");
    if (!email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) next.push("A valid email is required.");
    if (!subject.trim()) next.push("Subject is required.");
    if (!message.trim() || message.trim().length < 10) next.push("Message must be at least 10 characters.");
    return next;
  }

  function payload() {
    return {
      name: name.trim(),
      email: email.trim(),
      topic,
      subject: subject.trim(),
      message: message.trim(),
      pageUrl,
    };
  }

  function onMailto() {
    const next = validate();
    setErrors(next);
    setCopied(false);
    if (next.length) return;
    window.location.href = buildContactMailto(payload(), contact.public_email);
  }

  async function onCopy() {
    const next = validate();
    setErrors(next);
    if (next.length) return;
    const text = [
      `To: ${contact.public_email}`,
      `Topic: ${topic}`,
      `Subject: ${subject.trim()}`,
      `From: ${name.trim()} <${email.trim()}>`,
      `Page: ${pageUrl}`,
      "",
      message.trim(),
    ].join("\n");
    await navigator.clipboard.writeText(text);
    setCopied(true);
  }

  return (
    <>
      <PageIntro
        eyebrow="Contact"
        title="Write to the steward of Bhāva."
        body={`${contact.steward_name} · ${contact.location_city}, ${contact.location_state}. Messages open in your email app — Bhāva does not store form submissions.`}
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container contact-grid">
          <article className="contact-card">
            <p className="eyebrow">Message form</p>
            <h2>Send a note</h2>
            <p className="hint">
              Your email app opens with a prepared message. Nothing is uploaded to Bhāva servers.
              Do not include sensitive information about children.
            </p>
            <form
              className="contact-form"
              onSubmit={(e) => {
                e.preventDefault();
                onMailto();
              }}
              noValidate
            >
              <label>
                Name
                <input value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" required />
              </label>
              <label>
                Email
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" required />
              </label>
              <label>
                Topic
                <select value={topic} onChange={(e) => setTopic(e.target.value as (typeof TOPICS)[number])}>
                  {TOPICS.map((item) => (
                    <option key={item} value={item}>{item}</option>
                  ))}
                </select>
              </label>
              <label>
                Subject
                <input value={subject} onChange={(e) => setSubject(e.target.value)} required />
              </label>
              <label>
                Message
                <textarea value={message} onChange={(e) => setMessage(e.target.value)} rows={6} required />
              </label>
              {errors.length > 0 ? (
                <ul className="hint" role="alert">
                  {errors.map((err) => <li key={err}>{err}</li>)}
                </ul>
              ) : null}
              <div className="actions" style={{ marginTop: "1rem" }}>
                <button type="submit" className="bhava-button bhava-button--accent">Open in email app</button>
                <button type="button" className="bhava-button bhava-button--quiet" onClick={() => void onCopy()}>
                  Copy message
                </button>
              </div>
              {copied ? <p className="hint" aria-live="polite">Message copied. Paste it into your email if mailto is unavailable.</p> : null}
            </form>
          </article>
          <article className="contact-card">
            <p className="eyebrow">Steward</p>
            <h2>{contact.steward_name}</h2>
            <p><a href={`mailto:${contact.public_email}`}>{contact.public_email}</a></p>
            <p className="hint">{contact.location_city}, {contact.location_state}</p>
            <p style={{ marginTop: "1rem" }}>
              <Link href="/faq">FAQ</Link>
              {" · "}
              <Link href="/privacy">Privacy</Link>
              {" · "}
              <Link href="/source-permissions">Sources</Link>
            </p>
          </article>
        </div>
      </section>
    </>
  );
}
