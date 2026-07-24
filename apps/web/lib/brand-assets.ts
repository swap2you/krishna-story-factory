/** Brand asset helpers for wiring approved production WebP paths. */

export type BrandAsset = {
  logicalId: string;
  category?: string;
  productionPath: string;
  approvalState?: string;
  altPurpose?: string;
  width?: number;
  height?: number;
  responsiveVariants?: { width: number; path: string }[];
};

import registry from "@/config/brand-assets.json";

const assets = (registry as { assets: BrandAsset[] }).assets;

export function brandAsset(logicalId: string): BrandAsset | undefined {
  return assets.find((a) => a.logicalId === logicalId);
}

export function brandSrc(logicalId: string): string | undefined {
  return brandAsset(logicalId)?.productionPath;
}

export function brandSrcSet(logicalId: string): string | undefined {
  const asset = brandAsset(logicalId);
  if (!asset?.responsiveVariants?.length) return undefined;
  return asset.responsiveVariants.map((v) => `${v.path} ${v.width}w`).join(", ");
}

export function collectionCoverPath(slug: string): string | undefined {
  const map: Record<string, string> = {
    "krishna-book": "collection-krishna-book",
    "srimad-bhagavatam": "collection-srimad-bhagavatam",
    "bhagavad-gita": "collection-bhagavad-gita",
    ramayana: "collection-ramayana",
    "rama-katha": "collection-rama-katha",
    ramacaritamanasa: "collection-ramacaritamanasa",
    dasavatara: "collection-dasavatara",
    "caitanya-caritamrta": "collection-caitanya-caritamrta",
    "caitanya-bhagavata": "collection-caitanya-bhagavata",
    "prayers-mantras": "collection-prayers-mantras",
    "teacher-resources": "collection-teacher-resources",
    "sunday-school": "collection-sunday-school",
    printables: "collection-printables",
    knowledge: "collection-bhakti-blog",
    "bhakti-blog": "collection-bhakti-blog",
    vani: "collection-prabhupada-vani",
    "prabhupada-vani": "collection-prabhupada-vani",
  };
  const id = map[slug];
  return id ? brandSrc(id) : undefined;
}

export function cantoCoverPath(canto: number | string): string | undefined {
  const n = String(canto).padStart(2, "0");
  return brandSrc(`collection-canto-${n}`);
}
