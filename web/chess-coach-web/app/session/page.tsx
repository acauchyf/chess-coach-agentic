"use client";

import { useMemo, useState } from "react";
import { apiPost, apiGet } from "@/src/lib/api/client";
import { Board } from "@/src/components/ChessBoard";
import { Chess } from "chess.js";

type DailyPuzzle = {
  puzzle_id: number;
  area: string;
  game_id: string;
  ply: number;
  fen: string;
  hint: string;
  pv_uci: string[];
  tags: string[];
  attempts: number;
  solved: number;
};

type BootstrapResponse = {
  username: string;
  fatigue: number;
  puzzles: DailyPuzzle[];
  counts: { games: number; puzzles: number };
  decision: any;
};

type AttemptResponse = {
  correct: boolean;
  done: boolean;
  message: string;
  expected?: string | null;
};

export default function SessionPage() {
  const [username, setUsername] = useState("acauchy");
  const [platform, setPlatform] = useState<"lichess" | "chesscom">("lichess");

  const [data, setData] = useState<BootstrapResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);

  const [active, setActive] = useState<DailyPuzzle | null>(null);
  const [fen, setFen] = useState<string>("");
  const [message, setMessage] = useState<string>("");
  const [step, setStep] = useState<number>(0);

  // chat
  const [chatMsg, setChatMsg] = useState<string>("");
  const [chatReply, setChatReply] = useState<string>("");
  const [voiceEnabled, setVoiceEnabled] = useState<boolean>(false);

  const orientation = useMemo(() => {
    if (!active) return "white" as const;
    const ch = new Chess(active.fen);
    return ch.turn() === "w" ? "white" : "black";
  }, [active]);

  async function bootstrap() {
    setErr(null);
    setMessage("");
    try {
      const res = await apiPost<BootstrapResponse>("/coach/bootstrap", {
        platform,
        username,
        // fatigue omitted on purpose: agent will infer (or from existing checkin)
        import_games: 50,
        mine_blunders_from_games: 30,
        max_new_puzzles: 30,
        daily_limit: 10,
      });
      setData(res);
      if (res.puzzles.length > 0) {
        selectPuzzle(res.puzzles[0]);
      }
    } catch (e: any) {
      setErr(e.message ?? "error");
    }
  }

  function selectPuzzle(p: DailyPuzzle) {
    setActive(p);
    setFen(p.fen);
    setMessage(p.hint);
    setStep(0);
  }

  async function attemptMove(puzzleId: number, moveUci: string, currentStep: number): Promise<AttemptResponse> {
    return apiPost<AttemptResponse>(`/puzzles/${puzzleId}/attempt`, { move_uci: moveUci, step: currentStep });
  }

  function uciFromMove(from: string, to: string, promotion?: string) {
    return `${from}${to}${promotion ?? ""}`.toLowerCase();
  }

  function applyUci(ch: Chess, uci: string) {
    const from = uci.slice(0, 2);
    const to = uci.slice(2, 4);
    const promo = uci.length > 4 ? uci[4] : undefined;
    const mv = ch.move({ from, to, promotion: (promo as any) ?? "q" });
    return !!mv;
  }

  async function handleUserUci(userUci: string) {
    if (!active) return;

    const res = await attemptMove(active.puzzle_id, userUci, step);
    setMessage(res.message);

    if (!res.correct) {
      const reset = new Chess(active.fen);
      for (let i = 0; i < step; i++) applyUci(reset, active.pv_uci[i]);
      setFen(reset.fen());
      return;
    }

    let nextStep = step + 1;

    // auto-reply with PV opponent move if exists
    const ch = new Chess(fen);
    if (active.pv_uci[nextStep]) {
      const oppUci = active.pv_uci[nextStep];
      const ok = applyUci(ch, oppUci);
      if (ok) {
        setFen(ch.fen());
        nextStep += 1;
      }
    }

    setStep(nextStep);

    if (res.done || nextStep >= Math.max(1, active.pv_uci.length)) {
      setMessage("✅ Puzzle completado. Elige otro.");
    }
  }

  function onDrop(source: string, target: string) {
    if (!active) return false;

    try {
      const ch = new Chess(fen);
      const move = ch.move({ from: source, to: target, promotion: "q" });
      if (!move) return false;

      const uci = uciFromMove(source, target, move.promotion);
      setFen(ch.fen());
      void handleUserUci(uci);
      return true;
    } catch {
      return false;
    }
  }

  async function sendChat() {
    const msg = chatMsg.trim();
    if (!msg) return;
    setChatReply("");
    try {
      const res = await apiPost<{ reply: string }>("/coach/chat", { username, message: msg });
      setChatReply(res.reply);
      if (voiceEnabled && typeof window !== "undefined" && "speechSynthesis" in window) {
        try {
          const u = new SpeechSynthesisUtterance(res.reply);
          u.lang = "es-ES";
          window.speechSynthesis.cancel();
          window.speechSynthesis.speak(u);
        } catch {}
      }
    } catch (e: any) {
      setChatReply(e.message ?? "error");
    }
  }

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Sesión diaria</h1>

      <div className="flex flex-wrap gap-2 items-center">
        <input
          className="border rounded px-3 py-2"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="username"
        />

<select
  className="border rounded px-3 py-2"
  value={platform}
  onChange={(e) => setPlatform(e.target.value as any)}
  title="Fuente de partidas"
>
  <option value="lichess">Lichess</option>
  <option value="chesscom">Chess.com</option>
</select>
        <button className="border rounded px-3 py-2" onClick={bootstrap}>
          Bootstrap (import + mine + sesión)
        </button>
        <a className="border rounded px-3 py-2" href="/today">Plan de hoy</a>
        <a className="border rounded px-3 py-2" href="/plan">Plan semanal</a>
        <a className="border rounded px-3 py-2" href="/traces">Traces</a>
        <a className="border rounded px-3 py-2" href="/courses">Cursos</a>
        <a className="border rounded px-3 py-2" href="/diagnostics">Diagnóstico</a>
      </div>

      {err && <p className="text-red-600">{err}</p>}

      {data && (
        <p className="text-sm opacity-80">
          Games: <b>{data.counts.games}</b> · Puzzles: <b>{data.counts.puzzles}</b> · Fatiga inferida hoy: <b>{data.fatigue}</b>
        </p>
      )}

      <div className="grid md:grid-cols-[560px_1fr] gap-6 items-start">
        <div className="space-y-3">
          {active ? (
            <>
              <div className="border rounded p-3 space-y-2">
                <div className="font-medium">
                  [{active.area}] Game {active.game_id} · ply {active.ply} · step {step}/{Math.max(1, active.pv_uci.length)}
                </div>
                <div className="text-sm opacity-80">{message}</div>
                <div className="text-xs opacity-70">
                  tags: {active.tags?.length ? active.tags.join(", ") : "—"} · attempts: {active.attempts} · solved: {active.solved}
                </div>
              </div>

              <Board fen={fen} onDrop={(s, t) => onDrop(s, t)} boardOrientation={orientation} />
            </>
          ) : (
            <div className="border rounded p-4 opacity-70">Haz bootstrap para cargar puzzles.</div>
          )}

          <div className="border rounded p-3 space-y-2">
            <div className="font-semibold">Habla con tu coach</div>
            <div className="flex gap-2">
              <input
                className="border rounded px-3 py-2 w-full"
                value={chatMsg}
                onChange={(e) => setChatMsg(e.target.value)}
                placeholder="Ej: plan semanal / estoy cansado / curso peón aislado"
              />
              <button className="border rounded px-3 py-2" onClick={sendChat}>Enviar</button>
              <button className="border rounded px-3 py-2" onClick={() => setVoiceEnabled(v => !v)}>
                Voz: {voiceEnabled ? "ON" : "OFF"}
              </button>
            </div>
            {chatReply && <div className="text-sm opacity-90">{chatReply}</div>}
          </div>
        </div>

        <div className="space-y-3">
          <h2 className="text-lg font-semibold">Puzzles</h2>
          <div className="space-y-2">
            {data?.puzzles.map((p) => (
              <button
                key={p.puzzle_id}
                className={
                  "w-full text-left border rounded p-3 hover:bg-black/5 " +
                  (active?.puzzle_id === p.puzzle_id ? "bg-black/5" : "")
                }
                onClick={() => selectPuzzle(p)}
              >
                <div className="font-medium">
                  #{p.puzzle_id} [{p.area}] {p.tags?.length ? `(${p.tags[0]})` : ""}
                </div>
                <div className="text-xs opacity-70">
                  Game {p.game_id} · ply {p.ply} · line {p.pv_uci.length} · a:{p.attempts} s:{p.solved}
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
