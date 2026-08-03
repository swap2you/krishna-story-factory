import Link from "next/link";
import { collectionCoverPath } from "@/lib/brand-assets";
import { collectionFocalPosition } from "@/lib/collection-art";
import { getCollectionStatus, type CollectionStatus } from "@/lib/collection-readiness";

export function CollectionCard({
  href,
  slug,
  title,
  description,
  status,
}: {
  href: string;
  slug: string;
  title: string;
  description: string;
  status?: CollectionStatus;
}) {
  const resolvedStatus = status ?? getCollectionStatus(slug);
  const cover = collectionCoverPath(slug) ?? collectionCoverPath("krishna-book");
  const focalPosition = collectionFocalPosition(slug);
  return (
    <Link
      href={href}
      className={`collection-card collection-card--art${cover ? "" : " collection-card--panel"}`}
      data-contrast-safe="true"
    >
      {cover ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          className="collection-card__media"
          src={cover}
          alt=""
          width={800}
          height={1000}
          aria-hidden="true"
          style={{ objectPosition: focalPosition }}
        />
      ) : (
        <div className="collection-card__panel-fallback" aria-hidden="true" />
      )}
      <div className="collection-card__body">
        <h3>{title}</h3>
        <p>{description}</p>
        <span className={`editorial-status ${resolvedStatus === "active" ? "active" : "planned"}`}>
          {resolvedStatus === "active" ? "Active" : "Planned"}
        </span>
      </div>
    </Link>
  );
}
