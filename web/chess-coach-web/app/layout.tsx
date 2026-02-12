import "./globals.css";
import Link from "next/link";

export const metadata = { title: "Chess Coach", description: "Agentic chess coach" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className="min-h-screen">
        <header className="border-b p-4 flex gap-4">
          <Link href="/" className="font-semibold">Chess Coach</Link>
          <Link href="/session">Sesión</Link>
          <Link href="/puzzles">Puzzles</Link>
          <Link href="/plan">Plan</Link>
          <Link href="/traces">Traces</Link>
        </header>
        {children}
      </body>
    </html>
  );
}
