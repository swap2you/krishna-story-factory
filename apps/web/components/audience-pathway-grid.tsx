import Link from "next/link";
import { AGE_PATHWAYS } from "@/lib/age-pathways";

function PathwayGlyph({ id }: { id: string }) {
  const common = {
    width: 48,
    height: 48,
    viewBox: "0 0 48 48",
    fill: "none",
    "aria-hidden": true as const,
    className: "audience-pathway-card__glyph",
  };
  switch (id) {
    case "kaumara":
      return (
        <svg {...common}>
          <circle cx="24" cy="24" r="18" stroke="#c47a2c" strokeWidth="2" strokeDasharray="3 3" />
          <path d="M18 28c2 4 10 4 12 0" stroke="#8a4b12" strokeWidth="2" strokeLinecap="round" />
          <circle cx="18" cy="20" r="1.6" fill="#8a4b12" />
          <circle cx="30" cy="20" r="1.6" fill="#8a4b12" />
        </svg>
      );
    case "pauganda":
      return (
        <svg {...common}>
          <rect x="12" y="10" width="24" height="28" rx="4" stroke="#3f6d4f" strokeWidth="2" fill="#f7f1e4" />
          <path d="M18 20h12M18 26h10M18 32h8" stroke="#8a6a3a" strokeWidth="2" strokeLinecap="round" />
        </svg>
      );
    case "kaisora":
      return (
        <svg {...common}>
          <path d="M14 34V16l10-4 10 4v18" stroke="#12375e" strokeWidth="2.2" fill="#eef3f8" />
          <path d="M20 22h8M20 28h6" stroke="#5a7a9a" strokeWidth="2" strokeLinecap="round" />
        </svg>
      );
    case "yauvana":
      return (
        <svg {...common}>
          <path d="M24 10l4 10h10l-8 6 3 10-9-6-9 6 3-10-8-6h10z" stroke="#a14d3a" strokeWidth="1.8" fill="#f3c9c0" />
        </svg>
      );
    default:
      return (
        <svg {...common}>
          <path
            d="M24 36s-10-6-10-14a6 6 0 0 1 10-4 6 6 0 0 1 10 4c0 8-10 14-10 14z"
            fill="#f3c9c0"
            stroke="#a14d3a"
            strokeWidth="1.8"
          />
        </svg>
      );
  }
}

export function AudiencePathwayGrid() {
  return (
    <ul className="audience-pathway-grid" aria-label="Age-aware learning pathways">
      {AGE_PATHWAYS.map((pathway) => {
        const body = (
          <>
            <PathwayGlyph id={pathway.id} />
            <p className="audience-pathway-card__sanskrit">{pathway.sanskrit}</p>
            <h3>{pathway.publicTitle}</h3>
            <p className="audience-pathway-card__age">{pathway.ageLabel}</p>
            <p className="audience-pathway-card__desc">{pathway.description}</p>
            <span
              className={`editorial-status ${pathway.status === "active" ? "active" : "planned"}`}
            >
              {pathway.status === "active" ? "Ready now" : "Pathway growing"}
            </span>
          </>
        );

        if (pathway.href && pathway.status === "active") {
          return (
            <li key={pathway.id}>
              <Link
                href={pathway.href}
                className="audience-pathway-card audience-pathway-card--link"
                aria-label={`${pathway.publicTitle}: ${pathway.description}`}
              >
                {body}
              </Link>
            </li>
          );
        }

        return (
          <li key={pathway.id}>
            <div
              className="audience-pathway-card audience-pathway-card--static"
              aria-label={`${pathway.publicTitle}: ${pathway.description}. Pathway growing.`}
            >
              {body}
            </div>
          </li>
        );
      })}
    </ul>
  );
}
