"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

type Props = {
  mode: "login" | "session";
  role?: string;
  roles: string[];
  workflow?: string[];
};

export function StudioClient({ mode, role, roles, workflow }: Props) {
  const router = useRouter();
  const [selected, setSelected] = useState(roles[0] || "steward");
  const [token, setToken] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function login(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const res = await fetch("/api/studio/session", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ role: selected, bootstrap_token: token }),
      });
      if (!res.ok) {
        const data = (await res.json().catch(() => ({}))) as { detail?: string };
        throw new Error(data.detail || "Login failed");
      }
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setBusy(false);
    }
  }

  async function logout() {
    await fetch("/api/studio/session", { method: "DELETE" });
    router.refresh();
  }

  if (mode === "login") {
    return (
      <form onSubmit={login} className="prose" style={{ maxWidth: 520 }}>
        <h2>Bootstrap sign-in</h2>
        <p className="hint">
          Local secure bootstrap. Default token is the value of <code>BHAVA_STUDIO_BOOTSTRAP_TOKEN</code>
          {" "}(or <code>bhava-local-studio</code> when unset). Never use external auth providers for V1.4.
        </p>
        <label>
          Role
          <select value={selected} onChange={(e) => setSelected(e.target.value)} aria-label="Studio role">
            {roles.map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </label>
        <label style={{ display: "block", marginTop: "0.75rem" }}>
          Bootstrap token
          <input
            type="password"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            autoComplete="current-password"
            required
          />
        </label>
        {error ? <p role="alert">{error}</p> : null}
        <button className="bhava-button bhava-button--primary" type="submit" disabled={busy} style={{ marginTop: "1rem" }}>
          {busy ? "Signing in…" : "Enter studio"}
        </button>
      </form>
    );
  }

  return (
    <div>
      <p>
        Signed in as <strong>{role}</strong>.{" "}
        <button type="button" className="bhava-button bhava-button--quiet" onClick={() => void logout()}>
          Sign out
        </button>
      </p>
      {workflow?.length ? (
        <p className="hint">Workflow: {workflow.join(" → ")}</p>
      ) : null}
    </div>
  );
}
