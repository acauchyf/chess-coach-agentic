"use client";

import { useState } from "react";
import { apiGet } from "@/src/lib/api/client";

export default function CoursesPage() {
  const [username, setUsername] = useState("acauchy");
  const [topic, setTopic] = useState("Peón aislado (IQP)");
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState<string | null>(null);

  async function load() {
    setErr(null);
    setData(null);
    try {
      const res = await apiGet<any>(`/courses/adaptive/user?username=${encodeURIComponent(username)}&topic=${encodeURIComponent(topic)}&limit_examples=6`);
      // response contains {course, examples}
      setData(res);
      setData(res);
    } catch (e: any) {
      setErr(e.message ?? "error");
    }
  }

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Cursos</h1>
      <div className="flex gap-2 items-center">
        <input className="border rounded px-3 py-2" value={username} onChange={(e) => setUsername(e.target.value)} />
        <input className="border rounded px-3 py-2 w-full" value={topic} onChange={(e) => setTopic(e.target.value)} />
        <button className="border rounded px-3 py-2" onClick={load}>Cargar</button>
        <a className="border rounded px-3 py-2" href="/today">Plan hoy</a>
      </div>
      {err && <p className="text-red-600">{err}</p>}
      {data && (
        
        <div className="space-y-3">
          <div className="border rounded p-3">
            <div className="font-medium">{data.course?.topic ?? data.topic}</div>
            <div className="text-sm opacity-80">{data.course?.subtitle ?? data.subtitle}</div>
            <div className="text-sm opacity-70">Duración: {data.course?.estimated_minutes ?? data.estimated_minutes} min</div>
            {data.course?.metadata?.teacher_notes || data.course?.metadata?.llm_rules_and_mistakes || data.metadata?.llm_rules_and_mistakes && (
              <pre className="text-xs mt-2 whitespace-pre-wrap">{data.metadata.llm_rules_and_mistakes}</pre>
            )}
          </div>

          <div className="space-y-2">
            {(data.course?.lessons ?? data.lessons)?.map((l: any, i: number) => (
              <div key={i} className="border rounded p-3 space-y-2">
                <div className="font-semibold">{i+1}. {l.title}</div>
                <div className="text-sm"><b>Objetivos:</b> {l.objectives?.join(" · ")}</div>
                <div className="text-sm"><b>Ideas clave:</b> {l.key_ideas?.join(" · ")}</div>
                <div className="text-sm"><b>Errores típicos:</b> {l.common_mistakes?.join(" · ")}</div>
                <div className="text-sm"><b>Mini-quiz:</b> {l.mini_quiz?.join(" · ")}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </main>
  );
}
