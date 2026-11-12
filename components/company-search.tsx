"use client";

import { FormEvent, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

type Company = {
  ticker: string;
  company: string;
  sector: string;
  industry: string;
  country: string;
};

export default function CompanySearch({ companies }: { companies: Company[] }) {
  const router = useRouter();
  const [query, setQuery] = useState("");

  const matches = useMemo(() => {
    const value = query.trim().toLowerCase();
    if (!value) return companies.slice(0, 12);

    return [...companies]
      .filter((item) =>
        item.ticker.toLowerCase().includes(value) ||
        item.company.toLowerCase().includes(value)
      )
      .sort((a, b) => {
        const aExact = a.ticker.toLowerCase() === value ? 0 : 1;
        const bExact = b.ticker.toLowerCase() === value ? 0 : 1;
        if (aExact !== bExact) return aExact - bExact;

        const aStart =
          a.ticker.toLowerCase().startsWith(value) ||
          a.company.toLowerCase().startsWith(value)
            ? 0
            : 1;
        const bStart =
          b.ticker.toLowerCase().startsWith(value) ||
          b.company.toLowerCase().startsWith(value)
            ? 0
            : 1;
        return aStart - bStart || a.company.localeCompare(b.company);
      })
      .slice(0, 24);
  }, [companies, query]);

  function openTicker(ticker: string) {
    router.push(`/company/${ticker.toLowerCase()}`);
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    if (matches[0]) openTicker(matches[0].ticker);
  }

  return (
    <div className="company-finder">
      <form onSubmit={submit} className="search-form">
        <label htmlFor="company-search">Search company or ticker</label>
        <div className="search-row">
          <input
            id="company-search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Amazon, AMZN, MongoDB, MDB..."
            autoComplete="off"
          />
          <button type="submit" disabled={!matches.length}>Open research</button>
        </div>
      </form>

      <div className="search-results" aria-live="polite">
        {matches.map((item) => (
          <button
            type="button"
            className="company-result"
            key={item.ticker}
            onClick={() => openTicker(item.ticker)}
          >
            <span>
              <strong>{item.company}</strong>
              <small>{item.sector} · {item.industry}</small>
            </span>
            <b>{item.ticker}</b>
          </button>
        ))}
      </div>
    </div>
  );
}
