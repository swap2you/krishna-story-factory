import Link from "next/link";
import type { CSSProperties } from "react";
import { collectionCoverPath } from "@/lib/brand-assets";
import { getCollectionArt } from "@/lib/collection-art";
import { getCollectionStatus, type CollectionStatus } from "@/lib/collection-readiness";

export function CollectionCard({
  href,
  slug,
  title,
  description,
  status,
  interactive,
}: {
  href: string;
  slug: string;
  title: string;
  description: string;
  status?: CollectionStatus;
  /** When false, render a non-link shelf (planned taxonomy without published content). */
  interactive?: boolean;
}) {
  const resolvedStatus = status ?? getCollectionStatus(slug);
  const isInteractive = interactive ?? resolvedStatus === "active";
  const cover = collectionCoverPath(slug) ?? collectionCoverPath("krishna-book");
  const art = getCollectionArt(slug);
  // Focal positions via CSS vars only — avoid inline objectPosition so mobile
  // media queries can apply --collection-focal-mobile.
  const mediaStyle = {
    ["--collection-focal" as string]: art.objectPositionDesktop,
    ["--collection-focal-mobile" as string]:
      art.objectPositionMobile ?? art.objectPositionDesktop,
  } as CSSProperties;

  const className = [
    "collection-card",
    "collection-card--art",
    cover ? "" : "collection-card--panel",
    isInteractive ? "" : "collection-card--disabled",
  ]
    .filter(Boolean)
    .join(" ");

  const body = (
    <>
      {cover ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          className="collection-card__media"
          src={cover}
          alt=""
          width={800}
          height={1000}
          aria-hidden="true"
          style={mediaStyle}
        />
      ) : (
        <div className="collection-card__panel-fallback" aria-hidden="true" />
      )}
      <div className="collection-card__body">
        <h3>{title}</h3>
        <p>{description}</p>
        <span className={`editorial-status ${resolvedStatus === "active" ? "active" : "planned"}`}>
          {resolvedStatus === "active" ? "Available" : "Planned"}
        </span>
      </div>
    </>
  );

  if (!isInteractive) {
    return (
      <article
        className={className}
        data-contrast-safe="true"
        data-collection-slug={slug}
        data-planned="true"
      >
        {body}
      </article>
    );
  }

  return (
    <Link
      href={href}
      className={className}
      data-contrast-safe="true"
      data-collection-slug={slug}
    >
      {body}
    </Link>
  );
}
