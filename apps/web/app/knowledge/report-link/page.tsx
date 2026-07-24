import type { Metadata } from "next";
import Link from "next/link";
import contact from "@/config/contact.json";
import { PageIntro } from "@/components/page-intro";

export const metadata: Metadata = {
  title: "Report a broken link",
  description: "Private broken-link report for Bhāva Knowledge resources.",
};

export default function ReportBrokenLinkPage() {
  const mailto = `mailto:${contact.public_email}?subject=${encodeURIComponent("[Broken link] Knowledge")}&body=${encodeURIComponent(
    "Page URL:\nBroken link URL:\nWhat you expected:\n\nDo not include sensitive information about children.\n",
  )}`;
  return (
    <>
      <PageIntro
        eyebrow="Private report"
        title="Report a broken link"
        body="Reports are private and moderated. We never show a false success state — your email app carries the message."
      />
      <section className="section">
        <div className="container prose" style={{ maxWidth: 640 }}>
          <p>
            <a className="bhava-button bhava-button--primary" href={mailto}>Open in email app</a>
          </p>
          <p className="hint">
            Or copy a note to {contact.public_email}. <Link href="/knowledge">← Knowledge</Link>
          </p>
        </div>
      </section>
    </>
  );
}
