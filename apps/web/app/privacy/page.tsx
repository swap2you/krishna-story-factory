import { PageIntro } from "@/components/page-intro";

export default function PrivacyPage() {
  return <PageIntro eyebrow="Privacy" title="Your family’s privacy matters."><p>Bhāva is designed as a local-first learning portal. Notes saved from a story are stored only in this browser using local storage.</p><p>When the local catalog API is running, the app requests story metadata from it. This shell does not add analytics or send notes to a remote service.</p></PageIntro>;
}
