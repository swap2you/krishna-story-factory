import fs from "node:fs";
import path from "node:path";

export type DraftFactoryStatus = {
  available: boolean;
  run_id?: string;
  dry_run?: boolean;
  factory_version?: string;
  queue_size?: number;
  items_done?: number;
  items_blocked_or_duplicate?: number;
  completed_keys?: number;
  costs?: Record<string, number>;
  started_at?: string;
  finished_at?: string | null;
  prompt_ledger?: string;
  publication_authority: boolean;
  authority: {
    approve: boolean;
    merge: boolean;
    deploy: boolean;
    publish: boolean;
  };
  message: string;
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

function statusPath(): string {
  return path.join(knowledgeRoot(), "factory", "state", "draft_factory_status.json");
}

const NO_AUTH = {
  approve: false,
  merge: false,
  deploy: false,
  publish: false,
} as const;

export function getDraftFactoryStatus(): DraftFactoryStatus {
  const file = statusPath();
  if (!fs.existsSync(file)) {
    return {
      available: false,
      publication_authority: false,
      authority: { ...NO_AUTH },
      message: "No factory run status yet. Execute dry-run to populate.",
    };
  }
  try {
    const data = JSON.parse(fs.readFileSync(file, "utf8")) as Record<string, unknown>;
    const itemStates = (data.item_states || {}) as Record<string, { status?: string }>;
    const values = Object.values(itemStates);
    const done = values.filter((v) => v.status === "done").length;
    const blocked = values.filter(
      (v) => (v.status || "").startsWith("failed") || v.status === "duplicate_skipped",
    ).length;
    return {
      available: true,
      run_id: String(data.run_id || ""),
      dry_run: Boolean(data.dry_run),
      factory_version: String(data.factory_version || ""),
      queue_size: Number(data.queue_size || 0),
      items_done: done,
      items_blocked_or_duplicate: blocked,
      completed_keys: Array.isArray(data.completed_keys) ? data.completed_keys.length : 0,
      costs: (data.costs || {}) as Record<string, number>,
      started_at: data.started_at ? String(data.started_at) : undefined,
      finished_at: data.finished_at == null ? null : String(data.finished_at),
      prompt_ledger: data.prompt_ledger ? String(data.prompt_ledger) : undefined,
      publication_authority: false,
      authority: { ...NO_AUTH },
      message: "Read-only factory progress. No approve/merge/deploy/publish controls.",
    };
  } catch {
    return {
      available: false,
      publication_authority: false,
      authority: { ...NO_AUTH },
      message: "Factory status unreadable.",
    };
  }
}
