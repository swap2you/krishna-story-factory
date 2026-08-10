import fs from "node:fs";
import path from "node:path";

export type IntakeOcrState = "NONE" | "OCR_PENDING";

export type SourceIntakeItem = {
  sequence: number;
  original_filename: string;
  workspace_copy: string;
  status: string;
  notes: string;
  dossier_ready: boolean;
  ocr_state: IntakeOcrState;
  rights_cleared: boolean;
  public_allowed: boolean;
  last_reviewed: string | null;
};

export type SourceIntakeLedger = {
  schema_version: string;
  program: string;
  description?: string;
  items: SourceIntakeItem[];
};

export type SourceIntakeSummary = {
  total: number;
  by_status: Record<string, number>;
  ocr_pending: number;
  dossier_ready: number;
  rights_cleared: number;
  public_allowed: number;
};

function knowledgeRoot(): string {
  const candidates = [
    path.join(process.cwd(), "..", "..", "content", "knowledge"),
    path.join(process.cwd(), "content", "knowledge"),
    path.resolve(process.cwd(), "../../content/knowledge"),
  ];
  for (const c of candidates) {
    if (fs.existsSync(c)) return c;
  }
  return candidates[0];
}

function ledgerPath(): string {
  return path.join(knowledgeRoot(), "source_intake", "owner_pdf_inventory_v2.json");
}

export function loadSourceIntakeLedger(): SourceIntakeLedger | null {
  const file = ledgerPath();
  if (!fs.existsSync(file)) return null;
  try {
    return JSON.parse(fs.readFileSync(file, "utf8")) as SourceIntakeLedger;
  } catch {
    return null;
  }
}

export function listSourceIntakeItems(): SourceIntakeItem[] {
  const ledger = loadSourceIntakeLedger();
  if (!ledger?.items?.length) return [];
  return [...ledger.items].sort((a, b) => a.sequence - b.sequence);
}

export function getSourceIntakeSummary(): SourceIntakeSummary {
  const items = listSourceIntakeItems();
  const by_status: Record<string, number> = {};
  let ocr_pending = 0;
  let dossier_ready = 0;
  let rights_cleared = 0;
  let public_allowed = 0;
  for (const item of items) {
    by_status[item.status] = (by_status[item.status] || 0) + 1;
    if (item.ocr_state === "OCR_PENDING") ocr_pending += 1;
    if (item.dossier_ready) dossier_ready += 1;
    if (item.rights_cleared) rights_cleared += 1;
    if (item.public_allowed) public_allowed += 1;
  }
  return {
    total: items.length,
    by_status,
    ocr_pending,
    dossier_ready,
    rights_cleared,
    public_allowed,
  };
}
