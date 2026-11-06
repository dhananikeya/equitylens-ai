import fs from "node:fs";
import path from "node:path";

const jsonCache = new Map();

function readJson(relativePath, fallback = {}) {
  if (jsonCache.has(relativePath)) return jsonCache.get(relativePath);

  try {
    const filePath = path.join(process.cwd(), relativePath);
    const value = JSON.parse(fs.readFileSync(filePath, "utf8"));
    jsonCache.set(relativePath, value);
    return value;
  } catch {
    jsonCache.set(relativePath, fallback);
    return fallback;
  }
}

function recordTicker(key, value) {
  const explicit = String(value?.ticker || "").trim().toUpperCase();
  if (explicit) return explicit;

  const match = String(key || "").match(/\(([A-Z0-9.\-]+)\)\s*$/i);
  return match ? match[1].toUpperCase() : "";
}

function findRecord(dataset, ticker) {
  const normalized = String(ticker || "").trim().toUpperCase();
  for (const [key, value] of Object.entries(dataset || {})) {
    if (recordTicker(key, value) === normalized) {
      return { key, value };
    }
  }
  return { key: "", value: null };
}

function mergedRecord(handPath, generatedPath, ticker) {
  const generated = readJson(generatedPath, {});
  const hand = readJson(handPath, {});

  const generatedMatch = findRecord(generated, ticker);
  const handMatch = findRecord(hand, ticker);

  return {
    key: handMatch.key || generatedMatch.key || "",
    value: handMatch.value || generatedMatch.value || null,
    source: handMatch.value ? "curated" : generatedMatch.value ? "generated" : "unavailable",
  };
}

function secRecord(ticker) {
  const dataset = readJson("data/sec_filings.json", {});
  const normalized = String(ticker || "").trim().toUpperCase();

  for (const [key, value] of Object.entries(dataset || {})) {
    const candidate =
      String(value?.ticker || "").trim().toUpperCase() ||
      recordTicker(key, value);
    if (candidate === normalized) return value;
  }

  return null;
}

export function loadCompanyResearch(ticker) {
  const metrics = mergedRecord(
    "data/company_metrics.json",
    "data/generated_company_metrics.json",
    ticker
  );
  const quarterly = mergedRecord(
    "data/company_quarterly.json",
    "data/generated_company_quarterly.json",
    ticker
  );
  const analysis = mergedRecord(
    "data/company_analysis.json",
    "data/generated_company_analysis.json",
    ticker
  );
  const registration = mergedRecord(
    "data/company_s1.json",
    "data/generated_company_s1.json",
    ticker
  );
  const sec = secRecord(ticker);

  return {
    metrics: metrics.value,
    quarterly: quarterly.value,
    analysis: analysis.value,
    registration: registration.value,
    sec,
    provenance: {
      metrics: metrics.source,
      quarterly: quarterly.source,
      analysis: analysis.source,
      registration: registration.source,
    },
  };
}
