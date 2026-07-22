import Link from "next/link";
import { PageIntro } from "@/components/page-intro";

export default function TeachersPage() {
  return <PageIntro eyebrow="For teachers" title="Make room for wonder."><p>Bhāva is designed to support gentle story circles, family learning, and moments of reflection. Each Krishna Book story brings together a narration, reading view, printable activity, and source context.</p><p><Link href="/library">Explore the story library</Link></p></PageIntro>;
}
