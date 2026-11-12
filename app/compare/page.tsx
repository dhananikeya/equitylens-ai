import CompareTable, { type CompareCompany } from "@/components/compare-table";
import { loadCompanyUniverse } from "@/lib/company-universe";

function numeric(value: unknown) {
  if (value === null || value === undefined || value === "") return null;
  const parsed = Number(String(value).replace(/[%,$]/g, ""));
  return Number.isFinite(parsed) ? parsed : null;
}

export default function ComparePage() {
  const universe = loadCompanyUniverse();

  const companies: CompareCompany[] = universe.map((row) => ({
    ticker: String(row.Ticker || "").toUpperCase(),
    company: String(row.Company || ""),
    sector: String(row.Sector || ""),
    industry: String(row.Industry || ""),
    country: String(row.Country || ""),
    marketCap: numeric(row["Market Cap"]),
    pe: numeric(row["P/E"]),
    price: numeric(row.Price),
    change: numeric(row.Change)
  }));

  const sectors = new Set(companies.map((company) => company.sector).filter(Boolean));
  const industries = new Set(companies.map((company) => company.industry).filter(Boolean));

  return (
    <main className="shell compare-page">
      <section className="research-intro compare-intro">
        <p className="eyebrow">PEER RESEARCH</p>
        <h1>Compare the company <span>inside its market.</span></h1>
        <p className="lede">
          Filter the EquityLens universe by sector and industry, compare valuation and market context,
          then open any company for source-linked research.
        </p>
        <div className="compare-stats">
          <div><strong>{companies.length}</strong><span>companies</span></div>
          <div><strong>{sectors.size}</strong><span>sectors</span></div>
          <div><strong>{industries.size}</strong><span>industries</span></div>
        </div>
      </section>

      <CompareTable companies={companies} />

      <section className="methodology-note">
        <strong>Comparison context, not a recommendation.</strong>
        <p>
          Market cap, price, P/E, and daily move come from the current universe snapshot and may be delayed.
          Use Company Research for filing-backed financial and business analysis.
        </p>
      </section>
    </main>
  );
}
