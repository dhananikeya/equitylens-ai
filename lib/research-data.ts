import fs from "node:fs";
import path from "node:path";
import { loadCompanyUniverse } from "@/lib/company-universe";

type JsonRecord = Record<string, any>;

function readJsonFile(filename: string): JsonRecord {
  const filePath = path.join(process.cwd(), "data", filename);
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function indexByTicker(dataset: JsonRecord): Map<string, any> {
  const index = new Map<string, any>();
  for (const [key, value] of Object.entries(dataset)) {
    const ticker = String(value?.ticker || key.match(/\(([^)]+)\)$/)?.[1] || "")
      .toUpperCase()
      .trim();
    if (ticker) index.set(ticker, value);
  }
  return index;
}

export function getCompanyResearch(tickerInput: string) {
  const ticker = tickerInput.toUpperCase().trim();
  const universe = loadCompanyUniverse();
  const company = universe.find(
    (row) => String(row.Ticker).toUpperCase() === ticker
  );

  if (!company) return null;

  const metrics = indexByTicker(readJsonFile("company_metrics.json")).get(ticker) || {};
  const analysis = indexByTicker(readJsonFile("company_analysis.json")).get(ticker) || {};
  const quarterly = indexByTicker(readJsonFile("company_quarterly.json")).get(ticker) || {};
  const s1 = indexByTicker(readJsonFile("company_s1.json")).get(ticker) || {};
  const secSummary = readJsonFile("sec_summary.json");
  const sec = secSummary?.companies?.[ticker] || {};

  return {
    company,
    metrics,
    analysis,
    quarterly,
    s1,
    sec,
    secGeneratedAt: secSummary?.generated_at_utc || null
  };
}

export function getResearchDirectory() {
  return loadCompanyUniverse().map((company) => ({
    ticker: String(company.Ticker).toUpperCase(),
    company: company.Company,
    sector: company.Sector,
    industry: company.Industry,
    country: company.Country
  }));
}
