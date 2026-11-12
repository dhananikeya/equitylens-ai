"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

export type FilingRow = {
  ticker: string;
  company: string;
  form: string;
  filingDate: string;
  reportDate: string;
  description: string;
  url: string;
};

export default function FilingTracker({ filings }: { filings: FilingRow[] }) {
  const [query, setQuery] = useState("");
  const [form, setForm] = useState("");

  const forms = useMemo(
    () => Array.from(new Set(filings.map((row) => row.form).filter(Boolean))).sort(),
    [filings]
  );

  const rows = useMemo(() => {
    const q = query.trim().toLowerCase();
    return filings.filter((row) => {
      const matchesQuery =
        !q ||
        row.ticker.toLowerCase().includes(q) ||
        row.company.toLowerCase().includes(q) ||
        row.description.toLowerCase().includes(q);
      return matchesQuery && (!form || row.form === form);
    });
  }, [filings, query, form]);

  return (
    <section className="filings-workspace">
      <div className="filings-controls">
        <label>
          <span>Search filings</span>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ticker, company, or filing description"
          />
        </label>
        <label>
          <span>Form type</span>
          <select value={form} onChange={(e) => setForm(e.target.value)}>
            <option value="">All research forms</option>
            {forms.map((item) => <option value={item} key={item}>{item}</option>)}
          </select>
        </label>
      </div>

      <div className="filings-summary">
        <strong>{rows.length}</strong>
        <span>recent material filings shown</span>
      </div>

      <div className="filings-table" role="table" aria-label="Recent SEC filings">
        <div className="filings-table-head" role="row">
          <span>Company</span><span>Form</span><span>Filed</span><span>Report period</span><span>Description</span><span>Source</span>
        </div>
        {rows.map((row, index) => (
          <div className="filings-table-row" role="row" key={`${row.ticker}-${row.form}-${row.filingDate}-${index}`}>
            <div>
              <Link href={`/company/${row.ticker.toLowerCase()}`}>
                <strong>{row.ticker}</strong> {row.company}
              </Link>
            </div>
            <strong>{row.form}</strong>
            <span>{row.filingDate || "N/A"}</span>
            <span>{row.reportDate || "N/A"}</span>
            <span>{row.description || "SEC filing"}</span>
            <a href={row.url} target="_blank" rel="noreferrer">Open ↗</a>
          </div>
        ))}
      </div>
    </section>
  );
}
