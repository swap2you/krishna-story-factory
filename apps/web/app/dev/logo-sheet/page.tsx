"use client";

const LOGOS = [
  ["Primary horizontal", "/brand/logo-primary-horizontal.webp"],
  ["Compact horizontal", "/brand/logo-compact-horizontal.webp"],
  ["Small header (locked desktop)", "/brand/logo-small-header.webp"],
  ["Icon only", "/brand/logo-icon-only.webp"],
  ["Dark background (footer)", "/brand/logo-dark-bg.webp"],
  ["Stacked", "/brand/logo-stacked.webp"],
  ["Wordmark", "/brand/logo-wordmark.webp"],
  ["Mono navy", "/brand/logo-mono-navy.webp"],
];

/** Local comparison sheet — excluded from primary nav. */
export default function LogoSheetPage() {
  return (
    <main className="container" style={{ padding: "2rem 0 4rem" }}>
      <p className="eyebrow">Brand laboratory · not in nav</p>
      <h1>Logo contact sheet</h1>
      <p>Canonical approved exports vs application crops. Desktop header must use true-aspect small-header.</p>
      <div style={{ display: "grid", gap: "1.5rem" }}>
        {LOGOS.map(([label, src]) => (
          <figure key={src} style={{ background: "#f7f1e6", padding: "1rem", borderRadius: 12 }}>
            <figcaption><strong>{label}</strong> · <code>{src}</code></figcaption>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={src} alt={label} style={{ maxWidth: "100%", height: "auto", marginTop: 12 }} />
            <div style={{ display: "flex", gap: 24, marginTop: 12, alignItems: "end" }}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={src} alt="" height={24} style={{ height: 24, width: "auto" }} />
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={src} alt="" height={32} style={{ height: 32, width: "auto" }} />
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={src} alt="" height={48} style={{ height: 48, width: "auto" }} />
            </div>
          </figure>
        ))}
      </div>
      <section style={{ marginTop: "2rem" }}>
        <h2>Desktop header simulation</h2>
        <div style={{ display: "flex", alignItems: "center", gap: 12, padding: 12, background: "#fff" }}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/brand/logo-small-header.webp" alt="bhāva" height={32} style={{ height: 32, width: "auto" }} />
        </div>
        <h2>Mobile simulation</h2>
        <div style={{ display: "flex", alignItems: "center", gap: 12, padding: 12, background: "#fff" }}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/brand/logo-icon-only.webp" alt="" width={40} height={40} />
          <span className="wordmark">bh<span>ā</span>va</span>
        </div>
      </section>
    </main>
  );
}
