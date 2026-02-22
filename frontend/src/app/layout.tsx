import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Kardechat – Sabedoria Espírita ao seu alcance",
  description:
    "Converse com a sabedoria de Allan Kardec. Respostas baseadas nos 5 livros do Pentateuco Espírita.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className="antialiased">{children}</body>
    </html>
  );
}
