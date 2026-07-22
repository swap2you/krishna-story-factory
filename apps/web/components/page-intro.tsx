import type { ReactNode } from "react";

export function PageIntro({
  eyebrow,
  title,
  body,
  children,
}: {
  eyebrow: string;
  title: string;
  body?: string;
  children?: ReactNode;
}) {
  return (
    <>
      <section className="page-hero">
        <div className="container">
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
