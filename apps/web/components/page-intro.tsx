import type { ReactNode } from "react";

export function PageIntro({
  eyebrow,
  title,
  body,
  children,
  heroSrc,
  heroSrcSet,
  heroAlt = "",
}: {
  eyebrow: string;
  title: string;
  body?: string;
  children?: ReactNode;
  heroSrc?: string;
  heroSrcSet?: string;
  /** Empty string = decorative */
  heroAlt?: string;
}) {
  return (
    <>
      <section className={`page-hero${heroSrc ? " page-hero--media" : ""}`}>
        {heroSrc ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            className="page-hero__media"
            src={heroSrc}
            srcSet={heroSrcSet}
            sizes="100vw"
            alt={heroAlt}
            width={1600}
            height={800}
          />
        ) : null}
        <div className="container page-hero__copy">
          <p className="eyebrow">{eyebrow}</p>
          <h1>{title}</h1>
          {body ? <p>{body}</p> : null}
        </div>
      </section>
      {children ? (
        <section className="section">
          <div className="container prose">{children}</div>
        </section>
      ) : null}
    </>
  );
}
