# 15 — About / Contact / FAQ / Trust Pages

## Identity check (live DOM inspection)

`/contact`: extracted all `a[href^="mailto:"]` links and all email-shaped strings in the rendered page text.

- `mailto:svarnagaurangdas@gmail.com` — the only mailto link on the page
- No placeholder text (no "Your Name", "example@example.com", lorem ipsum, etc.) found

`/about`: page text confirms:

> Steward: Svarna Gauranga Das · Harrisburg, Pennsylvania

> Bhāva is independent stewardship, not an official BBT publication, and does not claim ownership of BBT source works.

`/privacy`: page text confirms:

> Steward: Svarna Gauranga Das.

All three identity surfaces (contact mailto, about, privacy) are internally consistent with each other and correctly reflect the operator identity — no leaked personal data beyond the intentionally-public steward name/contact, no default template placeholder content.

## `/contact` behavior

- Confirms client-side-only behavior: "Your email app opens with a prepared message. Nothing is uploaded to Bhāva servers."
- Explicit child-safety caution present: "Do not include sensitive information about children."
- Form fields: Name, Email, Topic (dropdown incl. Content correction, Devotional/source question, Teacher feedback, Technical issue, Suggestion, Other), Subject, Message; actions are "Open in email app" (mailto) and "Copy message" — both client-side, non-uploading actions. No server-side form submission was found (consistent with the "Nothing is uploaded" claim), so this review did not need to test or avoid a real submit action.

## `/privacy`

States plainly that family notes, classroom playlists, and reading preferences are stored in the browser (`localStorage`) only, and that "Bhāva does not upload child notes to a cloud account." This is consistent with what was independently observed on `/teachers` (the Classroom Playlist explicitly states "Saved on this device only").

## `/faq`

Rendered content answers "What is Bhāva?", "Who is it for?", "What ages?", "What are the sources?" plainly and consistently with `/about` and `/knowledge` copy (Krishna Book / Śrīmad-Bhāgavatam sourcing, Vedabase links, no full-text republication).

## `/accessibility`, `/source-permissions`

Both render (200); not deep-audited for prose content this session beyond route-liveness given time constraints, but no rendering errors observed.

## Verdict for this section

**PASS.** Identity, contact, and trust content is accurate, internally consistent, free of placeholder/template text, and free of any inadvertent PII beyond the intentionally-published steward identity.
