import type { Metadata } from "next";
import { getStories } from "@/lib/catalog";
import { PreachersWorkspace } from "@/components/preachers-workspace";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "For Preachers",
  description: "Select stories from the catalog, preview source references and outlines, and export materials for preaching programs.",
};

export default async function PreachersPage() {
  const stories = await getStories();
  return <PreachersWorkspace stories={stories} />;
}
