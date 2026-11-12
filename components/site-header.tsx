import Link from "next/link";

const navigation = [
  ["Home", "/"],
  ["Company Research", "/company"],
  ["Industry Comparison", "/compare"],
  ["Market Monitor", "/markets"],
  ["Filings", "/filings"],
  ["Learn", "/learn"]
];

export default function SiteHeader() {
  return (
    <header className="shell topbar">
      <Link href="/" className="brand">EquityLens AI</Link>
      <nav className="nav" aria-label="Primary navigation">
        {navigation.map(([label, href]) => (
          <Link key={href} href={href}>{label}</Link>
        ))}
      </nav>
    </header>
  );
}
