import Link from "next/link";
import contact from "@/config/contact.json";
import { PageIntro } from "@/components/page-intro";

export default function ContactPage() {
  return <PageIntro eyebrow="Contact" title="Let’s stay in touch."><p>Bhāva is stewarded by {contact.steward_name}. For questions, feedback, or partnership ideas, use the contact link below.</p><p><a className="bhava-button bhava-button--primary" href={contact.contact_url}>Contact {contact.steward_name}</a></p><p><a href={contact.website}>{contact.website}</a></p>{contact.public_email ? <p><a href={`mailto:${contact.public_email}`}>{contact.public_email}</a></p> : null}<p><Link href="/privacy">Read our privacy information</Link></p></PageIntro>;
}
