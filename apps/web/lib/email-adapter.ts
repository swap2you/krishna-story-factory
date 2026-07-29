/**
 * Future email-provider adapter boundary.
 * V1.2 uses encoded mailto + copy fallback only — no provider credentials.
 */
export type ContactPayload = {
  name: string;
  email: string;
  topic: string;
  subject: string;
  message: string;
  pageUrl: string;
};

export type EmailProviderResult =
  | { status: "mailto"; href: string }
  | { status: "copied" }
  | { status: "unsupported"; detail: string };

export interface EmailProviderAdapter {
  readonly id: string;
  composeMailto(payload: ContactPayload): string;
  /** Optional future: send via a configured provider. Must not invent success. */
  send?(payload: ContactPayload): Promise<EmailProviderResult>;
}

export function buildContactMailto(payload: ContactPayload, to: string): string {
  const body = [
    `Topic: ${payload.topic}`,
    `Subject: ${payload.subject}`,
    `From: ${payload.name} <${payload.email}>`,
    `Page: ${payload.pageUrl}`,
    "",
    payload.message,
  ].join("\n");
  const params = new URLSearchParams({
    subject: `[Bhāva] ${payload.topic}: ${payload.subject}`,
    body,
  });
  return `mailto:${to}?${params.toString()}`;
}

export const mailtoAdapter: EmailProviderAdapter = {
  id: "mailto",
  composeMailto: (payload) => buildContactMailto(payload, "svarnagaurangdas@gmail.com"),
};
