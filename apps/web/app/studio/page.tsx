"use client";

import { useEffect, useState } from "react";
import { Button, Card } from "@bhava/ui";
import { PageIntro } from "@/components/page-intro";

type Status = {
  loopback_only?: boolean;
  factory_actions_enabled?: boolean;
  csrf_token?: string;
};

export default function StudioPage() {
  const [status, setStatus] = useState<Status | null>(null);
  const [queue, setQueue] = useState<unknown>(null);
  const [message, setMessage] = useState("Studio loads only against 127.0.0.1.");

  async function refresh() {
    try {
      const [statusRes, queueRes] = await Promise.all([
        fetch("http://127.0.0.1:8000/api/v1/local/status"),
        fetch("http://127.0.0.1:8000/api/v1/local/queue"),
      ]);
      setStatus(statusRes.ok ? await statusRes.json() : null);
      setQueue(queueRes.ok ? await queueRes.json() : null);
      setMessage(statusRes.ok ? "Connected to local factory gateway." : "API not reachable on loopback.");
    } catch {
      setMessage("API not reachable on loopback.");
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  const enabled = Boolean(status?.factory_actions_enabled);

  async function post(path: string) {
    if (!enabled || !status?.csrf_token) {
      setMessage("Production actions are disabled (demo mode). Set BHAVA_FACTORY_ACTIONS_ENABLED=true only for intentional local ops.");
      return;
    }
    const response = await fetch(`http://127.0.0.1:8000/api/v1/local/${path}`, {
      method: "POST",
      headers: { "X-CSRF-Token": status.csrf_token, Origin: "http://127.0.0.1:3000" },
    });
    setMessage(await response.text());
  }

  return (
    <>
      <div className="local-banner">Local Factory Studio — loopback only · never expose publicly</div>
      <PageIntro
        eyebrow="Factory Studio"
        title="Safe operator console around the locked story factory."
        body="Read queue and health here. Generation buttons stay disabled unless you explicitly enable the local actions flag. This branch must not trigger Story 008."
      />
      <section className="section">
        <div className="container" style={{ display: "grid", gap: "1rem" }}>
          <Card className="story-content">
            <h2>Overview</h2>
            <p>{message}</p>
            <p>Actions enabled: {enabled ? "YES" : "NO (demo)"}</p>
            <p>Loopback enforced: {String(status?.loopback_only ?? "unknown")}</p>
            <Button onClick={() => void refresh()}>Refresh</Button>
          </Card>
          <Card className="story-content">
            <h2>Queue</h2>
            <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(queue, null, 2)}</pre>
          </Card>
          <Card className="story-content">
            <h2>Allowlisted operations</h2>
            <div className="actions">
              <Button variant="quiet" disabled={!enabled} onClick={() => void post("preflight")}>Preflight</Button>
              <Button variant="quiet" disabled={!enabled} onClick={() => void post("generate-next")}>Generate next</Button>
              <Button variant="quiet" disabled={!enabled} onClick={() => void post("drive/readback")}>Drive readback</Button>
            </div>
            <p className="hint">Disabled controls are intentional. Tests and default local runs never call paid providers.</p>
          </Card>
        </div>
      </section>
    </>
  );
}
