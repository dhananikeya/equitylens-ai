import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "EquityLens AI",
  description:
    "Source-linked public-company research using SEC filings, financial data, peer comparisons, and market context."
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
