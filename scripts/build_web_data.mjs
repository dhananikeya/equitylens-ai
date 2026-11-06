import fs from "node:fs";
import path from "node:path";
import { parse } from "csv-parse/sync";

const root = process.cwd();
const dataDir = path.join(root, "data");
const outputDir = path.join(root, "public", "research");

fs.mkdirSync(outputDir, { recursive: true });

function readJson(name) {
  try {
    return JSON.parse(fs.readFileSync(path.join(dataDir, name), "utf8"));
  } catch {
    return {};
  }
}

function recordTicker(key, value) {
  const explicit = String(value?.ticker || "").trim().toUpperCase();
  if (explicit) return explicit;
  const match = String(key || "").match(/\(([A-Z0-9.\-]+)\)\s*$/i);
  return match ? match[1].toUpperCase() : "";
}

function indexByTicker(dataset) {
  const output = new Map();
  for (const [key, value] of Object.entries(dataset || {})) {
    const ticker = recordTicker(key, value);
    if (ticker) output.set(ticker, value);
  }
  return output;
}

const universe = parse(
  fs.readFileSync(path.join(dataDir, "finviz_universe.csv"), "utf8"),
  {
    columns: true,
    skip_empty_lines: true,
    relax_quotes: true,
    relax_column_count: true,
  }
);

const handMetrics = indexByTicker(readJson("company_metrics.json"));
const generatedMetrics = indexByTicker(readJson("generated_company_metrics.json"));
const handQuarterly = indexByTicker(readJson("company_quarterly.json"));
const generatedQuarterly = indexByTicker(readJson("generated_company_quarterly.json"));
const handAnalysis = indexByTicker(readJson("company_analysis.json"));
const generatedAnalysis = indexByTicker(readJson("generated_company_analysis.json"));
const handS1 = indexByTicker(readJson("company_s1.json"));
const generatedS1 = indexByTicker(readJson("generated_company_s1.json"));
const sec = indexByTicker(readJson("sec_filings.json"));

let written = 0;

for (const row of universe) {
  const ticker = String(row.Ticker || "").trim().toUpperCase();
  if (!ticker) continue;

  const bundle = {
    ticker,
    metrics: handMetrics.get(ticker) || generatedMetrics.get(ticker) || null,
    quarterly: handQuarterly.get(ticker) || generatedQuarterly.get(ticker) || null,
    analysis: handAnalysis.get(ticker) || generatedAnalysis.get(ticker) || null,
    registration: handS1.get(ticker) || generatedS1.get(ticker) || null,
    sec: sec.get(ticker) || null,
    provenance: {
      metrics: handMetrics.has(ticker)
        ? "curated"
        : generatedMetrics.has(ticker)
          ? "generated"
          : "unavailable",
      quarterly: handQuarterly.has(ticker)
        ? "curated"
        : generatedQuarterly.has(ticker)
          ? "generated"
          : "unavailable",
      analysis: handAnalysis.has(ticker)
        ? "curated"
        : generatedAnalysis.has(ticker)
          ? "generated"
          : "unavailable",
      registration: handS1.has(ticker)
        ? "curated"
        : generatedS1.has(ticker)
          ? "generated"
          : "unavailable",
    },
  };

  fs.writeFileSync(
    path.join(outputDir, ticker + ".json"),
    JSON.stringify(bundle),
    "utf8"
  );
  written += 1;
}

console.log("Prepared " + written + " per-company research bundles.");
