import Link from "next/link";
import { getUniverseStats } from "@/lib/company-universe";

export default function HomePage() {
  const stats = getUniverseStats();

  return (
    <main>
      <section className="shell hero">
        <p className="eyebrow">PRIMARY-SOURCE PUBLIC COMPANY RESEARCH</p>
        <h1>
          Understand companies.
          <span> Not documents.</span>
        </h1>
        <p className="lede">
          EquityLens brings SEC filings, financial performance, business context,
          market data, and source-linked research into one workspace so investors,
          students, and curious humans can understand a company without excavating
          hundreds of pages manually.
        </p>

        <div className="stats" aria-label="Coverage statistics">
          <div><strong>{stats.companyCount}</strong><span>Companies</span></div>
          <div><strong>{stats.industryCount}</strong><span>Industries</span></div>
          <div><strong>{stats.sectorCount}</strong><span>Sectors</span></div>
          <div><strong>SEC</strong><span>Primary source first</span></div>
        </div>
      </section>

      <section className="shell grid">
        <Link href="/company" className="card">
          <p className="card-kicker">RESEARCH</p>
          <h2>Company Research</h2>
          <p>Financials, business context, risks, filings, ownership, analyst context, peers, and ETFs.</p>
        </Link>
        <Link href="/compare" className="card">
          <p className="card-kicker">COMPARE</p>
          <h2>Industry Comparison</h2>
          <p>Compare growth, margins, financial profiles, and business models across peers.</p>
        </Link>
        <Link href="/markets" className="card">
          <p className="card-kicker">MARKETS</p>
          <h2>Market Monitor</h2>
          <p>Market movement, heat maps, rates, economic releases, and macro context.</p>
        </Link>
        <Link href="/filings" className="card">
          <p className="card-kicker">DISCLOSURES</p>
          <h2>SEC Filing Tracker</h2>
          <p>Follow recent filings with direct links back to original SEC evidence.</p>
        </Link>
      </section>

      <footer className="shell footer">
        <span>Educational research, not investment advice.</span>
        <span>© 2026 Keya Dhanani</span>
      </footer>
    </main>
  );
}
