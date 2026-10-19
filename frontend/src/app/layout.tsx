import type { Metadata } from "next";
import Link from "next/link";
import { ThemeToggle } from "@/components/theme-toggle";
import "./globals.css";

export const metadata: Metadata = {
  title: "Game Theory Simulator",
  description: "Simulate and compare strategy tournaments across game-theory games.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" data-theme="dark" className="dark" suppressHydrationWarning>
      <body>
        <a className="skip-link" href="#main">
          Skip to content
        </a>
        <header className="app-header">
          <Link href="/">Game Theory Simulator</Link>
          <span>Prisoner’s Dilemma</span>
          <ThemeToggle />
        </header>
        {children}
      </body>
    </html>
  );
}
