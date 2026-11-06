import fs from "node:fs";
import path from "node:path";
import { parse } from "csv-parse/sync";

export function loadCompanyUniverse() {
  const csvPath = path.join(process.cwd(), "data", "finviz_universe.csv");
  const source = fs.readFileSync(csvPath, "utf8");
  const rows = parse(source, {
    columns: true,
    skip_empty_lines: true,
    relax_quotes: true,
    relax_column_count: true,
  });

  return rows
    .map((row) => ({
      ticker: String(row.Ticker || "").trim().toUpperCase(),
      company: String(row.Company || "").trim(),
      sector: String(row.Sector || "").trim(),
      industry: String(row.Industry || "").trim(),
      country: String(row.Country || "").trim(),
      marketCap: String(row["Market Cap"] || "").trim(),
      pe: String(row["P/E"] || "").trim(),
      price: String(row.Price || "").trim(),
      change: String(row.Change || "").trim(),
      volume: String(row.Volume || "").trim(),
    }))
    .filter((row) => row.ticker && row.company);
}
