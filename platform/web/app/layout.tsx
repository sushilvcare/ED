import "./globals.css";
import Link from "next/link";
import { ReactNode } from "react";

export const metadata = {
  title: "EdTech Course Platform",
  description: "Generate and sell feature-based engineering courses",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <main>
          <nav style={{ display: "flex", gap: 16, marginBottom: 20 }}>
            <Link href="/">Home</Link>
            <Link href="/catalog">Catalog</Link>
            <Link href="/dashboard">Dashboard</Link>
            <Link href="/admin">Admin</Link>
          </nav>
          {children}
        </main>
      </body>
    </html>
  );
}
