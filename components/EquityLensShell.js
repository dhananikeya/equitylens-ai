"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";

const NAV = [
  "Home",
  "Company Research",
  "Industry Comparison",
  "Market Monitor",
  "Filings",
  "Learn",
];

function normalize(value) {
  return String(value || "").toLowerCase().trim();
}

export default function EquityLensShell({ companies, industryCount }) {
  const router = useRouter();
  const [active, setActive] = useState("Home");
  const [query, setQuery] = useState("");
  const [selectedCompany, setSelectedCompany] = useState(null);

  const searchResults = useMemo(() => {
    const q = normalize(query);
    if (!q) return [];

    const sectionMatches = NAV.filter((item) =>
      normalize(item).includes(q)
    ).map((item) => ({ type: "section", label: item, value: item }));

    const companyMatches = companies
      .filter((company) => {
        return (
          normalize(company.ticker).includes(q) ||
          normalize(company.company).includes(q) ||
          normalize(company.industry).includes(q)
        );
      })
      .slice(0, 8)
      .map((company) => ({
        type: "company",
        label: company.ticker + " · " + company.company,
        meta: company.industry,
        value: company,
      }));

    return [...companyMatches, ...sectionMatches].slice(0, 10);
  }, [query, companies]);

  function selectSearchResult(result) {
    if (result.type === "company") {
      router.push("/company/" + result.value.ticker);
      return;
    }

    setActive(result.value);
    setQuery("");
  }

  return (
    <main className="app-shell">
      <div className="eyebrow">EquityLens AI · Free educational research</div>

      <div className="search-wrap">
        <input
          className="global-search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search companies, tickers, filings, markets, or sections…"
          aria-label="Search EquityLens"
        />
        {query && searchResults.length > 0 && (
          <div className="search-results">
            {searchResults.map((result, index) => (
              <button
                key={result.type + "-" + index}
                className="search-result"
                onClick={() => selectSearchResult(result)}
              >
                <span>{result.label}</span>
                {result.meta && <small>{result.meta}</small>}
              </button>
            ))}
          </div>
        )}
      </div>

      <nav className="top-nav" aria-label="EquityLens navigation">
        {NAV.map((item) => (
          <button
            key={item}
            className={active === item ? "nav-item active" : "nav-item"}
            onClick={() => setActive(item)}
          >
            {item}
          </button>
        ))}
      </nav>

      {active === "Home" && (
        <>
          <section className="hero">
            <div className="hero-kicker">Public-company research, made easier to navigate</div>
            <h1>
              Research public companies.
              <span>Without digging through hundreds of pages.</span>
            </h1>
            <p>
              EquityLens brings SEC filings, financial performance, business context,
              market data, and source-linked research into one workspace so you can
              understand a company faster and verify the original evidence yourself.
            </p>
            <div className="badges">
              <span>{companies.length.toLocaleString()}-company universe</span>
              <span>{industryCount.toLocaleString()} industries</span>
              <span>SEC EDGAR sourced</span>
              <span>Direct filing links</span>
            </div>
            <div className="creator">
              Independently created by Keya Dhanani · Educational research, not investment advice.
            </div>
          </section>

          <section className="metric-grid">
            <article className="metric-card">
              <small>Companies</small>
              <strong>{companies.length.toLocaleString()}</strong>
              <span>Broad public-company coverage</span>
            </article>
            <article className="metric-card">
              <small>Industries</small>
              <strong>{industryCount.toLocaleString()}</strong>
              <span>Cross-sector discovery</span>
            </article>
            <article className="metric-card">
              <small>Primary source</small>
              <strong>SEC EDGAR</strong>
              <span>Original filing links</span>
            </article>
            <article className="metric-card">
              <small>Research model</small>
              <strong>Source-linked</strong>
              <span>Reported, calculated, and summarized</span>
            </article>
          </section>

          <section className="section-block">
            <div className="section-label">START HERE</div>
            <h2>What would you like to explore?</h2>
            <div className="action-grid">
              {[
                ["Research a company", "Company Research", "Financials, business context, risks, and original filings."],
                ["Compare companies", "Industry Comparison", "Compare growth, margins, and business models across peers."],
                ["Explore markets", "Market Monitor", "Market movement, heat maps, rates, and economic releases."],
                ["Learn the basics", "Learn", "Plain-language explanations of financial terms and concepts."],
              ].map(([label, destination, description]) => (
                <button
                  key={destination}
                  className="action-card"
                  onClick={() => setActive(destination)}
                >
                  <strong>{label}</strong>
                  <span>{description}</span>
                </button>
              ))}
            </div>
          </section>
        </>
      )}

      {active === "Company Research" && (
        <section className="section-block">
          <div className="section-label">COMPANY RESEARCH</div>
          <h2>{selectedCompany ? selectedCompany.company : "Choose a company"}</h2>
          <p className="muted">
            Use the global search above to open any company in the 517-company universe.
            Each company now has its own shareable research page with financials, business
            context, risks, SEC filings, registration research, and capital-structure evidence.
          </p>
          <div className="company-directory-grid">
            {companies.slice(0, 12).map((company) => (
              <button
                key={company.ticker}
                className="directory-card"
                onClick={() => router.push("/company/" + company.ticker)}
              >
                <strong>{company.ticker}</strong>
                <span>{company.company}</span>
                <small>{company.industry}</small>
              </button>
            ))}
          </div>
        </section>
      )}

      {!["Home", "Company Research"].includes(active) && (
        <section className="section-block">
          <div className="section-label">{active.toUpperCase()}</div>
          <h2>{active}</h2>
          <p className="muted">
            This section is being migrated from the existing Streamlit application into
            the new Vercel frontend. The Streamlit version remains live while we port it.
          </p>
        </section>
      )}
    </main>
  );
}
