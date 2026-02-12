"use client";

import { useState } from "react";
import { apiGet } from "@/src/lib/api/client";

export default function PlanPage() {
  const [username, setUsername] = useState("acauchy");
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState<string | null>(null);

  async function load() {
    setErr(null);
    try {
      const res = await apiGet<any>(`/coach/weekly-plan?username=${encodeURIComponent(username)}`);
      setData(res);
    } catch (e: any) {
      setErr(e.message ?? "error");
    }
  }

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Plan semanal (personalizado)</h1>
      <div className="flex gap-2 items-center">
        <input className="border rounded px-3 py-2" value={username} onChange={(e) => setUsername(e.target.value)} />
        <button className="border rounded px-3 py-2" onClick={load}>Cargar</button>
      </div>
      {err && <p className="text-red-600">{err}</p>}
      {data && (
        <div className="space-y-4">
          <div className="border rounded p-3">
            <div className="font-medium">{data.headline}</div>
            <div className="text-sm opacity-70">Fatiga: {data.fatigue}/10</div>
            <div className="text-sm opacity-70">Focus tags: {data.focus_tags?.join(", ")}</div>
          </div>

          <div className="space-y-2">
            <div className="font-semibold">Bloques</div>
            {data.blocks?.map((b: any, i: number) => (
              <div key={i} className="border rounded p-3">
                <div className="font-medium">[{b.area}] {b.title} — {b.duration_min} min</div>
                <div className="text-sm opacity-80">{b.why}</div>
              </div>
            ))}
          </div>

          <div className="space-y-2">
            <div className="font-semibold">Cursos sugeridos (estructuras)</div>
            {data.courses?.length ? data.courses.map((c: any, i: number) => (
              <div key={i} className="border rounded p-3">
                <div className="font-medium">{c.topic} — {c.recommended_minutes} min</div>
                <div className="text-sm opacity-80">{c.why}</div>
              </div>
            )) : <div className="opacity-70">Aún no detecté estructuras fuertes. (Se refina con más partidas)</div>}
          </div>
        </div>
      )}
    </main>
  );
}
