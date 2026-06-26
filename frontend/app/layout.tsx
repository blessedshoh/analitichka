import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "NBU Market Review — Newsletter Generator",
  description: "Type the news, click one button, get the PDF.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
