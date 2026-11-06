import "./globals.css";

export const metadata = {
  title: "EquityLens AI",
  description:
    "SEC-linked public-company research across a 517-company coverage universe.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
