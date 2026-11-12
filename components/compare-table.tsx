"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

export type CompareCompany = {
  ticker: string;
  company: string;
  sector: string;
  industry: string;
  country: string;
  marketCap: number | null;
  pe: number | null;
  price: number | null;
  change: number | null;
};

function money(value: number | null) {
  if (value === null || !Number.isFinite(value)) return "N/A";
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(2)}T`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(1)}B`;
  return `$${value.toFixed(1)}M`;
}

export default function CompareTable({ companies }: { companies: CompareCompany[] }) {
  const sectors = useMemo(
    () => Array.from(new Set(companies.map((c) => c.sector).filter(Boolean))).sort(),
    [companies]
  );
  const [sector, setSector] = useState("");
  const industries = useMemo(
    () =>
      Array.from(
        new Set(
          companies
            .filter((c) => !sector || c.sector === sector)
            .map((c) => c.industry)
            .filter(Boolean)
        )
      ).sort(),
    [companies, sector]
  );
  const [industry, setIndustry] = useState("");
  const [query, setQuery] = useState("");

  const rows = useMemo(() => {
    const q = query.trim().toLowerCase();
    return companies
      .filter((c) => !sector || c.sector === sector)
      .filter((c) => !industry || c.industry === industry)
      .filter((c) => !q || c.ticker.toLowerCase().includes(q) || c.company.toLowerCase().includes(q))
      .sort((a, b) => (b.marketCap || 0) - (a.marketCap || 0))
      .slice(0, 100);
  }, [companies, sector, industry, query]);

  return (
    <section className="compare-workspace">
      <div className="compare-controls">
        <label>
          <span>Sector</span>
          <select value={sector} onChange={(e) => { setSector(e.target.value); setIndustry(""); }}>
            <option value="">All sectors</option>
            {sectors.map((item) => <option value={item} key={item}>{item}</option>)}
          </select>
        </label>
        <label>
          <span>Industry</span>
          <select value={industry} onChange={(e) => setIndustry(e.target.value)}>
            <option value="">All industries</option>
            {industries.map((item) => <option value={item} key={item}>{item}</option>)}
          </select>
        </label>
        <label className="compare-search">
          <span>Find company</span>
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Ticker or company" />
        </label>
      </div>

      <div className="compare-summary">
        <strong>{rows.length}</strong>
        <span>companies shown</span>
      </div>

      <div className="compare-table" role="table" aria-label="Industry comparison">
        <div className="compare-table-head" role="row">
          <span>Company</span><span>Sector / Industry</span><span>Market cap</span><span>P/E</span><span>Price</span><span>Daily move</span>
        </div>
        {rows.map((row) => (
          <div className="compare-table-row" role="row" key={row.ticker}>
            <div>
              <Link href={`/company/${row.ticker.toLowerCase()}`}><strong>{row.ticker}</strong> {row.company}</Link>
              <small>{row.country || "Country unavailable"}</small>
            </div>
            <span>{row.sector}<small>{row.industry}</small></span>
            <strong>{money(row.marketCap)}</strong>
            <span>{row.pe === null ? "N/A" : row.pe.toFixed(2)}</span>
            <span>{row.price === null ? "N/A" : `$${row.price.toFixed(2)}`}</span>
            <span className={row.change === null ? "" : row.change >= 0 ? "market-up" : "market-down"}>
              {row.change === null ? "N/A" : `${row.change >= 0 ? "+" : ""}${row.change.toFixed(2)}%`}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
