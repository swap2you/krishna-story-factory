import { PageIntro } from "@/components/page-intro";

export default function StudioPage() {
  return <><div className="local-banner">Factory Studio is local-only. It does not publish, send messages, or call paid services from this portal.</div><PageIntro eyebrow="Factory Studio" title="A local workspace for story preparation."><p>This is a deliberately limited studio shell. The existing Krishna Story Factory CLI remains the source of truth for production work and approvals.</p><p>Story generation controls are intentionally unavailable here until an approved local integration is enabled.</p></PageIntro></>;
}
