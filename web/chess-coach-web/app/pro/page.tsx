"use client";

import { useState } from "react";
import { apiGet } from "@/src/lib/api/client";

export default function ProPage() {
  const [username, setUsername] = useState("acauchy");
  const [diag, setDiag] = useState<any>(null);
  const [week, setWeek] = useState<any>(null);
  const [err, setErr] = useState<string | null>(null);

  async function load() {
    setErr(null);
    try {
      const d = await apiGet<any>(`/pro/diagnostics?username=${encodeURIComponent(username)}`);
      const w = await apiGet<any>(`/pro/curriculum/weekly?username=${encodeURIComponent(username)}`);
      setDiag(d);
      setWeek(w);
    } catch (e: any) {
      setErr(e.message ?? "error");
    }
  }

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">MVP 1 PRO (Coach)</h1>
      <div className="flex gap-2 items-center">
        <input className="border rounded px-3 py-2" value={username} onChange={(e) => setUsername(e.target.value)} />
        <button className="border rounded px-3 py-2" onClick={load}>Cargar</button>
        <a className="border rounded px-3 py-2" href="/today">Plan hoy</a>
        <a className="border rounded px-3 py-2" href="/courses">Cursos</a>
      </div>

      {err && <p className="text-red-600">{err}</p>}

      {diag?.phase?.summary && (
        <div className="border rounded p-3 space-y-2">
          <div className="font-semibold">Diagnóstico por fases (proxy desde blunders)</div>
          <div className="text-sm">Apertura avg swing: {diag.phase.summary.opening_avg_swing.toFixed(1)} cp · Blunders: {diag.phase.summary.opening_blunders}</div>
          <div className="text-sm">Medio juego avg swing: {diag.phase.summary.middlegame_avg_swing.toFixed(1)} cp · Blunders: {diag.phase.summary.middlegame_blunders}</div>
          <div className="text-sm">Final avg swing: {diag.phase.summary.endgame_avg_swing.toFixed(1)} cp · Blunders: {diag.phase.summary.endgame_blunders}</div>
          <div className="text-sm opacity-70">Partidas analizadas: {diag.phase.summary.games_analyzed}</div>
        </div>
      )}

      {diag?.conversion && (
        <div className="border rounded p-3">
          <div className="font-semibold">Conversión (heurística)</div>
          <div className="text-sm">Con ventaja en {diag.conversion.total_advantaged} partidas · Fallos: {diag.conversion.failed_conversions}</div>
          <div className="text-sm">Tasa: {(diag.conversion.conversion_rate*100).toFixed(0)}%</div>
        </div>
      )}

      {diag?.opening_breakpoints?.length ? (
        <div className="border rounded p-3 space-y-2">
          <div className="font-semibold">Breakpoints de apertura (primer swing grande)</div>
          {diag.opening_breakpoints.slice(0, 10).map((b: any, i: number) => (
            <div key={i} className="text-sm">
              {b.opening_name} · move {b.move_number} · {b.count} veces · avg swing {b.avg_swing.toFixed(0)} cp
            </div>
          ))}
        </div>
      ) : null}

      {week?.days?.length ? (
        <div className="border rounded p-3 space-y-2">
          <div className="font-semibold">Curriculum semanal</div>
          <div className="text-sm opacity-80">Inicio: {week.start_date}</div>
          <div className="text-sm"><b>Goals:</b> {week.goals?.join(" · ")}</div>
          <div className="text-sm opacity-70">Revisiones programadas: {week.meta?.scheduled_reviews} · Tags débiles: {week.meta?.weak_tags?.join(", ")}</div>
          <div className="space-y-2">
            {week.days.map((d: any, idx: number) => (
              <div key={idx} className="border rounded p-2">
                <div className="font-medium">{d.day}</div>
                {d.blocks.map((b: any, j: number) => (
                  <div key={j} className="text-sm opacity-90">• [{b.type}] {b.title} — {b.minutes} min</div>
                ))}
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </main>
  );
}
