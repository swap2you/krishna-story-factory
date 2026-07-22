import Link from "next/link";
import { ErrorState } from "@bhava/ui";
import { getStories } from "@/lib/catalog";
import { StoryGrid } from "@/components/story-grid";

export default async function LibraryPage() {
  try {
    const stories = await getStories();
    return <><section className="page-hero"><div className="container"><p className="eyebrow">The library</p><h1>Return to Krishna’s pastimes.</h1><p>Browse the Krishna Book sequence in a calm, family-friendly format.</p></div></section><section className="section"><div className="container"><StoryGrid stories={stories} /></div></section></>;
  } catch {
    return <><section className="page-hero"><div className="container"><p className="eyebrow">The library</p><h1>Return to Krishna’s pastimes.</h1></div></section><section className="section"><div className="container"><ErrorState title="The local story catalog is unavailable"><p>Start the Bhāva API at 127.0.0.1:8000, then refresh this page.</p><Link href="/library/krishna-book">View the Krishna Book collection</Link></ErrorState></div></section></>;
  }
}
