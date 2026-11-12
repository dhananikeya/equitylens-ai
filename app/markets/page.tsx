import MarketBoard, { type MarketRow } from "@/components/market-board";
import { loadCompanyUniverse } from "@/lib/company-universe";

function numeric(value: unknown) {
  if (value === null || value === undefined || value === "") return null;
  const parsed = Number(String(value).replace(/[%,$]/g, ""));
  return Number.isFinite(parsed) ? parsed : null;
}

export default function MarketsPage() {
  const universe = loadCompanyUniverse();

  const rows: MarketRow[] = universe.map((row) => ({
    ticker: String(row.Ticker || "").toUpperCase(),
    company: String(row.Company || ""),
    sector: String(row.Sector || ""),
    marketCap: numeric(row["Market Cap"]),
    price: numeric(row.Price),
    change: numeric(row.Change),
    volume: numeric(row.Volume)
  }));

  const advancers = rows.filter((row) => (row.change || 0) > 0).length;
  const decliners = rows.filter((row) => (row.change || 0) < 0).length;
  const unchanged = rows.length - advancers - decliners;

  return (
    <main className="shell markets-page">
      <section className="research-intro markets-intro">
        <p className="eyebrow">MARKET MONITOR</p>
        <h1>See the market <span>before reading the story.</span></h1>
        <p className="lede">
          EquityLens pairs company research with a broad market snapshot so price action,
          sector leadership, and valuation context stay separate from filing-backed fundamentals.
        </p>

        <div className="market-breadth">
          <div><strong>{rows.length}</strong><span>companies</span></div>
          <div><strong>{advancers}</strong><span>advancing</span></div>
          <div><strong>{decliners}</strong><span>declining</span></div>
          <div><strong>{unchanged}</strong><span>unchanged</span></div>
        </div>
        <p className="feed-timestamp">Universe market snapshot may be delayed. Open Company Research for refreshed single-name context.</p>
      </section>

      <MarketBoard rows={rows} />

      <section className="macro-context">
        <article>
          <p className="eyebrow">RATES</p>
          <h2>Rates & liquidity</h2>
          <p>
            Treasury yields, SOFR, and curve context remain part of the migration plan.
            The Vercel version will surface them from the same public-source hierarchy used by the Streamlit app.
          </p>
        </article>
        <article>
          <p className="eyebrow">MACRO</p>
          <h2>Economic context</h2>
          <p>
            Inflation, labor, Federal Reserve updates, and release calendars will appear here with source timestamps and outbound links.
          </p>
        </article>
      </section>

      <section className="methodology-note">
        <strong>Market data is context.</strong>
        <p>
          Snapshot price, change, volume, and market capitalization fields may be delayed or stale.
          Filing-backed research and SEC documents remain the source of truth for company fundamentals.
        </p>
      </section>
    </main>
  );
}
