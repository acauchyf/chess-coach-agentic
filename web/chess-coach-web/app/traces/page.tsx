"use client";

import { useState } from "react";
import { apiGet } from "@/src/lib/api/client";

export default function TracesPage() {
  const [username, setUsername] = useState("acauchy");
  const [items, setItems] = useState<any[]>([]);
  const [err, setErr] = useState<string | null>(null);

  async function load() {
    setErr(null);
    try {
      const res = await apiGet<any>(`/coach/traces?username=${encodeURIComponent(username)}&limit=30`);
      setItems(res.items ?? []);
    } catch (e: any) {
      setErr(e.message ?? "error");
    }
  }

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Traces (6_mcp style)</h1>
      <div className="flex gap-2 items-center">
        <input className="border rounded px-3 py-2" value={username} onChange={(e) => setUsername(e.target.value)} />
        <button className="border rounded px-3 py-2" onClick={load}>Cargar</button>
      </div>
      {err && <p className="text-red-600">{err}</p>}
      <div className="space-y-2">
        {items.map((t, i) => (
          <div key={i} className="border rounded p-3">
            <div className="font-medium">{t.intent} · fatigue {t.fatigue}</div>
            <div className="text-xs opacity-70">{t.created_at}</div>
            <pre className="text-xs mt-2 whitespace-pre-wrap">{JSON.stringify(t.decision, null, 2)}</pre>
          </div>
        ))}
      </div>
    </main>
  );
}
