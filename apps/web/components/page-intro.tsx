import type { ReactNode } from "react";

export function PageIntro({ eyebrow, title, children }: { eyebrow: string; title: string; children: ReactNode }) {
  return <><section className="page-hero"><div className="container"><p className="eyebrow">{eyebrow}</p><h1>{title}</h1></div></section><section className="section"><div className="container prose">{children}</div></section></>;
}
