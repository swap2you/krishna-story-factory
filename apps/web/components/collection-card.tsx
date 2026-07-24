import Link from "next/link";
import { collectionCoverPath } from "@/lib/brand-assets";

export function CollectionCard({
  href,
  slug,
  title,
  description,
  status = "planned",
}: {
  href: string;
  slug: string;
  title: string;
  description: string;
  status?: "active" | "planned";
}) {
  const cover = collectionCoverPath(slug) ?? collectionCoverPath("krishna-book");
  return (
    <Link href={href} className="collection-card collection-card--art">
      {cover ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img className="collection-card__media" src={cover} alt="" width={800} height={1000} aria-hidden="true" />
      ) : null}
      <div className="collection-card__body">
        <h3>{title}</h3>
        <p>{description}</p>
        <span className={`editorial-status ${status === "active" ? "active" : "planned"}`}>
          {status === "active" ? "Active" : "Planned"}
        </span>
      </div>
    </Link>
  );
}
