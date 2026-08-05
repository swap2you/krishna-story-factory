/**
 * Per-collection art focus metadata for CollectionCard crops.
 * Prefer CSS object-position over regenerating images.
 */

export type CollectionArtConfig = {
  objectPositionDesktop: string;
  objectPositionMobile?: string;
  focalX?: number;
  focalY?: number;
};

const COLLECTION_ART: Record<string, CollectionArtConfig> = {
  "krishna-book": {
    objectPositionDesktop: "center 18%",
    objectPositionMobile: "center 22%",
    focalX: 0.5,
    focalY: 0.18,
  },
  "srimad-bhagavatam": {
    objectPositionDesktop: "center 28%",
    objectPositionMobile: "center 30%",
  },
  "bhagavad-gita": {
    objectPositionDesktop: "center 22%",
    objectPositionMobile: "center 25%",
  },
  ramayana: {
    objectPositionDesktop: "center 28%",
    objectPositionMobile: "center 30%",
  },
  "rama-katha": {
    objectPositionDesktop: "center 28%",
    objectPositionMobile: "center 30%",
  },
  ramacaritamanasa: {
    objectPositionDesktop: "center 32%",
    objectPositionMobile: "center 35%",
  },
  dasavatara: {
    objectPositionDesktop: "center 40%",
    objectPositionMobile: "center center",
  },
  "caitanya-caritamrta": {
    objectPositionDesktop: "center 22%",
    objectPositionMobile: "center 25%",
  },
  "caitanya-bhagavata": {
    objectPositionDesktop: "center 22%",
    objectPositionMobile: "center 25%",
  },
  "prayers-mantras": {
    objectPositionDesktop: "center 35%",
    objectPositionMobile: "center 40%",
  },
  "teacher-resources": {
    objectPositionDesktop: "center 30%",
    objectPositionMobile: "center 28%",
    focalX: 0.5,
    focalY: 0.3,
  },
  "sunday-school": {
    objectPositionDesktop: "center 32%",
    objectPositionMobile: "center 35%",
  },
  printables: {
    objectPositionDesktop: "center 40%",
    objectPositionMobile: "center center",
  },
  knowledge: {
    objectPositionDesktop: "center 35%",
    objectPositionMobile: "center 38%",
  },
  "prabhupada-vani": {
    objectPositionDesktop: "center 18%",
    objectPositionMobile: "center 20%",
    focalX: 0.5,
    focalY: 0.18,
  },
  "devotee-lives": {
    objectPositionDesktop: "center 30%",
    objectPositionMobile: "center center",
  },
};

const FALLBACK: CollectionArtConfig = {
  objectPositionDesktop: "center center",
  objectPositionMobile: "center center",
};

export function getCollectionArt(slug: string): CollectionArtConfig {
  return COLLECTION_ART[slug] ?? FALLBACK;
}

/** @deprecated Prefer getCollectionArt(slug).objectPositionDesktop */
export function collectionFocalPosition(slug: string): string {
  return getCollectionArt(slug).objectPositionDesktop;
}
