/**
 * Per-collection CSS object-position for cover images.
 * Ensures face/subject centering in CollectionCard thumbnails.
 */
const FOCAL_POSITIONS: Record<string, string> = {
  "krishna-book": "center 20%",
  "srimad-bhagavatam": "center 30%",
  "bhagavad-gita": "center 25%",
  ramayana: "center 30%",
  "rama-katha": "center 30%",
  ramacaritamanasa: "center 35%",
  dasavatara: "center center",
  "caitanya-caritamrta": "center 25%",
  "caitanya-bhagavata": "center 25%",
  "prayers-mantras": "center center",
  "teacher-resources": "center 35%",
  "sunday-school": "center center",
  printables: "center center",
  knowledge: "center center",
  "prabhupada-vani": "center 20%",
  "devotee-lives": "center center",
};

export function collectionFocalPosition(slug: string): string {
  return FOCAL_POSITIONS[slug] ?? "center center";
}
