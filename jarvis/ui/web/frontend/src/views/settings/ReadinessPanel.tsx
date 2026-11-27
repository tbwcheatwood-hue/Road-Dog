import { useEffect, useState } from "react";

type Check = {
  name: string;
  status: string;
  state?: string;
  detail: string;
  fix?: string | null;
};

type Area = { overall: string; checks: Check[] };

type Report = {
  _overall?: string;
  _sam_greeting?: string;
  model_connectivity?: Area;
};

const STATE_CLASS: Record<string, string> = {
  operational: "text-foreground",
  configured: "text-muted-foreground",
  installed: "text-muted-foreground",
  reachable: "text-muted-foreground",
  unavailable: "text-muted-foreground",
  unverified: "text-muted-foreground",
};

/** Settings and onboarding view of GET /api/setup-report/diagnostics. */
export function ReadinessPanel() {
  const [report, setReport] = useState<Report | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), 15000);
    fetch("/api/setup-report/diagnostics", { signal: controller.signal })
      .then(async (response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        setReport((await response.json()) as Report);
      })
      .catch((exc: unknown) => {
        setError(exc instanceof Error ? exc.message : "Readiness did not load.");
      })
      .finally(() => window.clearTimeout(timer));
    return () => controller.abort();
  }, []);

  const checks = report?.model_connectivity?.checks ?? [];
  return (
    <section className="rounded-lg border border-border bg-card p-3 text-sm text-foreground" data-testid="readiness-panel">
      <h3 className="font-medium">Readiness</h3>
      <p className="mt-1 text-muted-foreground">
        {report?._sam_greeting ||
          "Installed, configured, and answering are separate. A stored key is not a successful login."}
      </p>
      {error ? <p className="mt-2 text-muted-foreground">{error}</p> : null}
      <ul className="mt-2 space-y-2">
        {checks.map((check) => (
          <li key={check.name}>
            <span className={STATE_CLASS[check.state || "unverified"] || "text-muted-foreground"}>
              {check.state || "unverified"}
            </span>
            <span className="ml-2">{check.name}</span>
            <p className="text-muted-foreground">{check.detail}</p>
            {check.fix ? <p className="text-muted-foreground">{check.fix}</p> : null}
          </li>
        ))}
      </ul>
    </section>
  );
}
