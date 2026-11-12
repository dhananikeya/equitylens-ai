"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

export type MarketRow = {
  ticker: string;
  company: string;
  sector: string;
  marketCap: number | null;
  price: number | null;
  change: number | null;
  volume: number | null;
};

function capText(value: number | null) {
  if (value === null || !Number.isFinite(value)) return "N/A";
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(2)}T`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(1)}B`;
  return `$${value.toFixed(0)}M`;
}

export default function MarketBoard({ rows }: { rows: MarketRow[] }) {
  const sectors = useMemo(
    () => Array.from(new Set(rows.map((row) => row.sector).filter(Boolean))).sort(),
    [rows]
  );
  const [sector, setSector] = useState("");
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return rows
      .filter((row) => !sector || row.sector === sector)
      .filter((row) => !q || row.ticker.toLowerCase().includes(q) || row.company.toLowerCase().includes(q))
      .sort((a,b) => (b.marketCap || 0) - (a.marketCap || 0))
      .slice(0, 120);
  }, [rows, sector, query]);

  const tape = useMemo(
    () => [...rows].sort((a,b) => (b.volume || 0) - (a.volume || 0)).slice(0, 20),
    [rows]
  );

  return (
    <>
      <section className="market-tape-shell" aria-label="Market snapshot tape">
        <div className="market-tape-label">MARKET SNAPSHOT</div>
        <div className="market-tape-track">
          {[...tape, ...tape].map((row, index) => (
            <Link href={`/company/${row.ticker.toLowerCase()}`} className="market-tape-item" key={`${row.ticker}-${index}`}>
              <strong>{row.ticker}</strong>
              <span>{row.price === null ? "N/A" : `$${row.price.toFixed(2)}`}</span>
              <b className={row.change === null ? "" : row.change >= 0 ? "market-up" : "market-down"}>
                {row.change === null ? "N/A" : `${row.change >= 0 ? "+" : ""}${row.change.toFixed(2)}%`}
              </b>
            </Link>
          ))}
        </div>
      </section>

      <section className="market-board">
        <div className="market-board-head">
          <div>
            <p className="eyebrow">MARKET MAP</p>
            <h2>Universe heat map</h2>
            <p>Larger tiles represent larger market capitalization. Tile tone represents the current snapshot move.</p>
          </div>
          <div className="market-board-controls">
            <select value={sector} onChange={(e) => setSector(e.target.value)} aria-label="Filter by sector">
              <option value="">All sectors</option>
              {sectors.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
            <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Find ticker" aria-label="Find ticker" />
          </div>
        </div>

        <div className="heat-grid">
          {filtered.map((row) => {
            const size = Math.max(1, Math.min(4, Math.ceil(Math.log10(Math.max(10, row.marketCap || 10)) - 2)));
            const move = row.change || 0;
            const tone =
              move >= 3 ? "heat-strong-up" :
              move > 0 ? "heat-up" :
              move <= -3 ? "heat-strong-down" :
              move < 0 ? "heat-down" : "heat-flat";
            return (
              <Link
                href={`/company/${row.ticker.toLowerCase()}`}
                className={`heat-tile ${tone}`}
                style={{ gridColumn: `span ${size}`, gridRow: `span ${size}` }}
                key={row.ticker}
              >
                <strong>{row.ticker}</strong>
                <span>{row.company}</span>
                <b>{row.change === null ? "N/A" : `${row.change >= 0 ? "+" : ""}${row.change.toFixed(2)}%`}</b>
                <small>{capText(row.marketCap)}</small>
              </Link>
            );
          })}
        </div>
      </section>
    </>
  );
}
