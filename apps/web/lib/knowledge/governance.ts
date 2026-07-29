import { validateResourceDraft, TYPE_TEMPLATES } from "./types";

export function assertNoPublicLeak(records: { lifecycle: string; visibility: string }[]): void {
  for (const row of records) {
    if (row.visibility !== "public") {
      throw new Error(`Non-public roadmap row leaked: ${JSON.stringify(row)}`);
    }
    if (!["approved", "published"].includes(row.lifecycle)) {
      throw new Error(`Non-published lifecycle leaked: ${JSON.stringify(row)}`);
    }
  }
}

export { validateResourceDraft, TYPE_TEMPLATES };
