"use client";

import { useEffect, useState } from "react";
import { apiPost } from "@/src/lib/api/client";

type Plan = {
  headline: string;
  fatigue: number;
  minutes: number;
  blocks: { area: string; title: string; duration_min: number; why: string }[];
  courses: any[];
  focus_tags: string[];
};

function formatMMSS(sec: number) {
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

export default function TodayPage() {
  const [username, setUsername] = useState("acauchy");
  const [minutes, setMinutes] = useState(45);
  const [data, setData] = useState<Plan | null>(null);
  const [err, setErr] = useState<string | null>(null);

  const [activeIdx, setActiveIdx] = useState<number | null>(null);
  const [remaining, setRemaining] = useState<number>(0);

  useEffect(() => {
    if (activeIdx === null) return;
    if (remaining <= 0) return;
    const t = setInterval(() => setRemaining((r) => r - 1), 1000);
    return () => clearInterval(t);
  }, [activeIdx, remaining]);

  async function load() {
    setErr(null);
    setData(null);
    setActiveIdx(null);
    try {
      const res = await apiPost<Plan>("/coach/today", { username, minutes });
      setData(res);
    } catch (e: any) {
      setErr(e.message ?? "error");
    }
  }

  function start(i: number) {
    if (!data) return;
    setActiveIdx(i);
    setRemaining(data.blocks[i].duration_min * 60);
  }

  function stop() {
    setActiveIdx(null);
    setRemaining(0);
  }

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Plan de hoy (Profesor)</h1>

      <div className="flex flex-wrap gap-2 items-center">
        <input className="border rounded px-3 py-2" value={username} onChange={(e) => setUsername(e.target.value)} />
        <input
          type="number"
          min={10}
          max={180}
          className="border rounded px-3 py-2 w-24"
          value={minutes}
          onChange={(e) => setMinutes(Number(e.target.value))}
        />
        <button className="border rounded px-3 py-2" onClick={load}>Generar plan</button>
        <a className="border rounded px-3 py-2" href="/session">Sesión</a>
      </div>

      {err && <p className="text-red-600">{err}</p>}

      {data && (
        <>
          <div className="border rounded p-3">
            <div className="font-medium">{data.headline}</div>
            <div className="text-sm opacity-70">Fatiga estimada: {data.fatigue}/10 · Tiempo: {data.minutes} min</div>
            <div className="text-sm opacity-70">Foco: {data.focus_tags?.join(", ")}</div>
          </div>

          {activeIdx !== null && (
            <div className="border rounded p-3 flex items-center justify-between">
              <div>
                <div className="font-medium">⏱️ En curso: {data.blocks[activeIdx].title}</div>
                <div className="text-sm opacity-70">[{data.blocks[activeIdx].area}]</div>
              </div>
              <div className="text-2xl font-mono">{formatMMSS(Math.max(0, remaining))}</div>
              <button className="border rounded px-3 py-2" onClick={stop}>Parar</button>
            </div>
          )}

          <div className="space-y-2">
            <div className="font-semibold">Tareas</div>
            {data.blocks.map((b, i) => (
              <div key={i} className="border rounded p-3">
                <div className="font-medium">[{b.area}] {b.title} — {b.duration_min} min</div>
                <div className="text-sm opacity-80">{b.why}</div>
                <button className="border rounded px-3 py-2 mt-2" onClick={() => start(i)}>Empezar este bloque</button>
              </div>
            ))}
          </div>
        
<div className="space-y-2">
  <div className="font-semibold">Recomendaciones del profesor</div>
  {(data as any).recommended_courses?.length ? (data as any).recommended_courses.map((c: any, i: number) => (
    <div key={i} className="border rounded p-3">
      <div className="font-medium">{c.topic} — {c.minutes} min · urgencia {(c.urgency*100).toFixed(0)}%</div>
      <div className="text-sm opacity-80">{c.rationale}</div>
    </div>
  )) : <div className="opacity-70">Aún no hay recomendaciones (se afina con más datos).</div>}
</div>

        </>
      )}
    </main>
  );
}
