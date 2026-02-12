"use client";

import { useState } from "react";
import { apiGet } from "@/src/lib/api/client";

export default function DiagnosticsPage() {
  const [username, setUsername] = useState("acauchy");
  const [data, setData] = useState<any>(null);
  const [recs, setRecs] = useState<any>(null);
  const [err, setErr] = useState<string | null>(null);

  async function load() {
    setErr(null);
    setData(null);
    setRecs(null);
    try {
      const d = await apiGet<any>(`/diagnostics?username=${encodeURIComponent(username)}`);
      const r = await apiGet<any>(`/diagnostics/recommendations?username=${encodeURIComponent(username)}&max_items=6`);
      setData(d);
      setRecs(r);
    } catch (e: any) {
      setErr(e.message ?? "error");
    }
  }

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Diagnóstico (Profesor)</h1>
      <div className="flex gap-2 items-center">
        <input className="border rounded px-3 py-2" value={username} onChange={(e) => setUsername(e.target.value)} />
        <button className="border rounded px-3 py-2" onClick={load}>Analizar</button>
        <a className="border rounded px-3 py-2" href="/today">Plan hoy</a>
        <a className="border rounded px-3 py-2" href="/courses">Cursos</a>
      </div>

      {err && <p className="text-red-600">{err}</p>}

      {recs?.items && (
        <div className="border rounded p-3 space-y-2">
          <div className="font-semibold">Recomendaciones (urgencia)</div>
          {recs.items.map((x: any, i: number) => (
            <div key={i} className="border rounded p-2">
              <div className="font-medium">{x.topic} — urgencia {(x.urgency*100).toFixed(0)}%</div>
              <div className="text-sm opacity-80">{x.rationale} ({x.minutes} min)</div>
            </div>
          ))}
        </div>
      )}

      {data?.signals && (
        <div className="space-y-2">
          <div className="font-semibold">Señales</div>
          {data.signals.slice(0, 20).map((s: any, i: number) => (
            <div key={i} className="border rounded p-2">
              <div className="font-medium">{s.label} — {(s.score*100).toFixed(0)}%</div>
              <pre className="text-xs whitespace-pre-wrap opacity-80">{JSON.stringify(s.evidence, null, 2)}</pre>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
