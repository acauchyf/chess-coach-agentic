"use client";

import { useState } from "react";
import { apiGet } from "@/src/lib/api/client";

type Puzzle = {
  puzzle_id: number;
  game_id: string;
  ply: number;
  fen: string;
  played_uci: string;
  best_uci: string;
  swing_cp: number;
};

export default function PuzzlesPage() {
  const [username, setUsername] = useState("acauchy");
  const [items, setItems] = useState<Puzzle[]>([]);
  const [err, setErr] = useState<string | null>(null);

  async function load() {
    setErr(null);
    try {
      const res = await apiGet<{ items: Puzzle[] }>(`/puzzles?username=${encodeURIComponent(username)}&limit=50`);
      setItems(res.items);
    } catch (e: any) {
      setErr(e.message ?? "error");
    }
  }

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Puzzles (raw)</h1>
      <div className="flex gap-2 items-center">
        <input className="border rounded px-3 py-2" value={username} onChange={(e) => setUsername(e.target.value)} />
        <button className="border rounded px-3 py-2" onClick={load}>Cargar</button>
      </div>
      {err && <p className="text-red-600">{err}</p>}
      <ul className="space-y-2">
        {items.map(p => (
          <li key={p.puzzle_id} className="border rounded p-3">
            <div className="font-medium">#{p.puzzle_id} · swing {p.swing_cp}cp</div>
            <div className="text-xs opacity-70">Game {p.game_id} · ply {p.ply}</div>
            <div className="text-xs break-all mt-1">best: {p.best_uci} · played: {p.played_uci}</div>
          </li>
        ))}
      </ul>
    </main>
  );
}
