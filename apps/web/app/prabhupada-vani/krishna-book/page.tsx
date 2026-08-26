import type { Metadata } from "next";
import Link from "next/link";
import { PageIntro } from "@/components/page-intro";
import { VaniCatalog } from "@/components/vani/vani-catalog";
import { loadVaniCollection } from "@/lib/vani";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Krishna Book Dictation Archive",
  description: "An ordered, provenance-aware catalog of Śrīla Prabhupāda's Krishna Book dictations.",
  robots: { index: false, follow: false },
};

export default async function VaniKrishnaBookPage() {
  const state = await loadVaniCollection();
  const collection = state.status === "ok" ? state.data : null;
  return (
    <>
      <PageIntro
        eyebrow="Prabhupāda Vāṇī · Krishna Book"
        title="The Krishna Book dictations, in chapter order."
        body="Listen to available source recordings without concealing historical gaps. Progress and bookmarks remain private to this device."
      />
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <nav className="vani-breadcrumb" aria-label="Breadcrumb">
            <Link href="/prabhupada-vani">Prabhupāda Vāṇī</Link><span aria-hidden="true">/</span><span>Krishna Book</span>
          </nav>
          {collection && collection.tracks.length > 0 ? (
            <VaniCatalog collection={collection} />
          ) : (
            <div className="coming" role="status">
              <div>
                <p className="eyebrow">Archive not open yet</p>
                <h2>The catalog is being prepared.</h2>
                <p>
                  No verified recordings are available from the archive API right now. Nothing has been
                  substituted or made playable. Please return after source and rights review.
                </p>
              </div>
            </div>
          )}
        </div>
      </section>
    </>
  );
}
