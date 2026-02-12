"use client";

import { Chessboard } from "react-chessboard";

export function Board({ fen, onDrop, boardOrientation }: {
  fen: string;
  onDrop: (sourceSquare: string, targetSquare: string, piece: string) => boolean;
  boardOrientation: "white" | "black";
}) {
  return (
    <div className="w-[360px] sm:w-[420px] md:w-[520px]">
      <Chessboard
        position={fen}
        onPieceDrop={(s, t, p) => onDrop(s, t, p)}
        boardOrientation={boardOrientation}
        arePiecesDraggable={true}
      />
    </div>
  );
}
