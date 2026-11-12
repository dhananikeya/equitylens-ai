import fs from "node:fs";
import path from "node:path";
import { loadCompanyUniverse } from "@/lib/company-universe";

type JsonRecord = Record<string, any>;

function readJsonFile(filename: string): JsonRecord {
  const filePath = path.join(process.cwd(), "data", filename);
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function tickerFromEntry(key: string, value: any) {
  return String(
    value?.ticker ||
    key.match(/\(([^)]+)\)$/)?.[1] ||
    ""
  ).toUpperCase().trim();
}

function companyNameFromKey(key: string, ticker: string) {
  const stripped = key.replace(/\s*\([^)]*\)\s*$/, "").trim();
  return stripped || ticker;
}

function indexByTicker(dataset: JsonRecord): Map<string, any> {
  const index = new Map<string, any>();
  for (const [key, value] of Object.entries(dataset)) {
    const ticker = tickerFromEntry(key, value);
    if (ticker) index.set(ticker, value);
  }
  return index;
}

function loadDatasets() {
  return {
    metricsRaw: readJsonFile("company_metrics.json"),
    analysisRaw: readJsonFile("company_analysis.json"),
    quarterlyRaw: readJsonFile("company_quarterly.json"),
    s1Raw: readJsonFile("company_s1.json"),
    secSummary: readJsonFile("sec_summary.json")
  };
}

function curatedIdentity(
  ticker: string,
  datasets: ReturnType<typeof loadDatasets>
) {
  for (const dataset of [
    datasets.metricsRaw,
    datasets.analysisRaw,
    datasets.quarterlyRaw,
    datasets.s1Raw
  ]) {
    for (const [key, value] of Object.entries(dataset)) {
      if (tickerFromEntry(key, value) !== ticker) continue;
      return {
        Ticker: ticker,
        Company: companyNameFromKey(key, ticker),
        Sector: String((value as any)?.sector || ""),
        Industry: String((value as any)?.industry || ""),
        Country: String((value as any)?.country || "")
      };
    }
  }
  return null;
}

export function getCompanyResearch(tickerInput: string) {
  const ticker = tickerInput.toUpperCase().trim();
  const universe = loadCompanyUniverse();
  const datasets = loadDatasets();

  const universeCompany = universe.find(
    (row) => String(row.Ticker).toUpperCase() === ticker
  );
  const company = universeCompany || curatedIdentity(ticker, datasets);

  if (!company) return null;

  const metrics = indexByTicker(datasets.metricsRaw).get(ticker) || {};
  const analysis = indexByTicker(datasets.analysisRaw).get(ticker) || {};
  const quarterly = indexByTicker(datasets.quarterlyRaw).get(ticker) || {};
  const s1 = indexByTicker(datasets.s1Raw).get(ticker) || {};
  const sec = datasets.secSummary?.companies?.[ticker] || {};

  return {
    company,
    metrics,
    analysis,
    quarterly,
    s1,
    sec,
    secGeneratedAt: datasets.secSummary?.generated_at_utc || null,
    isCoreUniverse: Boolean(universeCompany)
  };
}

export function getResearchDirectory() {
  const universe = loadCompanyUniverse();
  const datasets = loadDatasets();
  const directory = new Map<string, {
    ticker: string;
    company: string;
    sector: string;
    industry: string;
    country: string;
    isCoreUniverse: boolean;
  }>();

  for (const company of universe) {
    const ticker = String(company.Ticker).toUpperCase();
    directory.set(ticker, {
      ticker,
      company: company.Company,
      sector: company.Sector,
      industry: company.Industry,
      country: company.Country,
      isCoreUniverse: true
    });
  }

  for (const dataset of [
    datasets.metricsRaw,
    datasets.analysisRaw,
    datasets.quarterlyRaw,
    datasets.s1Raw
  ]) {
    for (const [key, value] of Object.entries(dataset)) {
      const ticker = tickerFromEntry(key, value);
      if (!ticker || directory.has(ticker)) continue;
      directory.set(ticker, {
        ticker,
        company: companyNameFromKey(key, ticker),
        sector: String((value as any)?.sector || ""),
        industry: String((value as any)?.industry || ""),
        country: String((value as any)?.country || ""),
        isCoreUniverse: false
      });
    }
  }

  return Array.from(directory.values()).sort((a, b) =>
    a.company.localeCompare(b.company)
  );
}
