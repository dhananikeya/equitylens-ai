import fs from "node:fs";
import path from "node:path";
import FilingTracker, { type FilingRow } from "@/components/filing-tracker";

function loadSecSummary() {
  const filePath = path.join(process.cwd(), "data", "sec_summary.json");
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

export default function FilingsPage() {
  const summary = loadSecSummary();
  const filings: FilingRow[] = Array.isArray(summary?.recent_filings)
    ? summary.recent_filings.map((row: any) => ({
        ticker: String(row.ticker || "").toUpperCase(),
        company: String(row.company || ""),
        form: String(row.form || ""),
        filingDate: String(row.filing_date || ""),
        reportDate: String(row.report_date || ""),
        description: String(row.description || ""),
        url: String(row.url || "")
      }))
    : [];

  return (
    <main className="shell filings-page">
      <section className="research-intro filings-intro">
        <p className="eyebrow">SEC MONITOR</p>
        <h1>Track material filings <span>without digging through EDGAR.</span></h1>
        <p className="lede">
          Recent research-relevant filings from the EquityLens SEC pipeline, including annual reports,
          quarterly reports, current reports, registration filings, and foreign issuer equivalents.
        </p>

        <div className="filings-stats">
          <div><strong>{summary?.company_count || 0}</strong><span>companies monitored</span></div>
          <div><strong>{summary?.synced_companies || 0}</strong><span>companies synced</span></div>
          <div>
            <strong>{filings.length}</strong>
            <span>recent material filings</span>
          </div>
        </div>

        <p className="feed-timestamp">
          SEC feed generated{" "}
          {summary?.generated_at_utc
            ? new Date(summary.generated_at_utc).toLocaleString("en-US", { timeZone: "America/New_York" }) + " ET"
            : "timestamp unavailable"}
        </p>
      </section>

      <FilingTracker filings={filings} />

      <section className="methodology-note">
        <strong>Primary source first.</strong>
        <p>
          Filing links point to original SEC documents. EquityLens surfaces recent material forms for research convenience,
          but the SEC filing itself remains the authoritative record.
        </p>
      </section>
    </main>
  );
}
