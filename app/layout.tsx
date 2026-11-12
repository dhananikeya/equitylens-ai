import type { Metadata } from "next";
import SiteHeader from "@/components/site-header";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://equitylens-ai-web.vercel.app"),
  title: {
    default: "EquityLens AI",
    template: "%s | EquityLens AI"
  },
  description:
    "Source-linked public-company research using SEC filings, financial data, peer comparisons, market context, and plain-language learning tools.",
  applicationName: "EquityLens AI",
  keywords: [
    "SEC filings",
    "company research",
    "10-K",
    "10-Q",
    "public companies",
    "financial analysis",
    "market research"
  ],
  openGraph: {
    type: "website",
    title: "EquityLens AI",
    description:
      "Understand public companies using source-linked SEC research, financial context, peer comparison, and market data.",
    siteName: "EquityLens AI"
  },
  twitter: {
    card: "summary_large_image",
    title: "EquityLens AI",
    description:
      "Source-linked public-company research built around SEC filings and understandable financial context."
  },
  robots: {
    index: true,
    follow: true
  }
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <a className="skip-link" href="#main-content">Skip to main content</a>
        <SiteHeader />
        <div id="main-content">{children}</div>
      </body>
    </html>
  );
}
