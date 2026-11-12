import fs from "node:fs";
import path from "node:path";
import Papa from "papaparse";

export type CompanyUniverseRow = {
  Ticker: string;
  Company: string;
  Sector: string;
  Industry: string;
  Country: string;
  [key: string]: string;
};

export function loadCompanyUniverse(): CompanyUniverseRow[] {
  const filePath = path.join(process.cwd(), "data", "finviz_universe.csv");
  const csv = fs.readFileSync(filePath, "utf8");
  const parsed = Papa.parse<CompanyUniverseRow>(csv, {
    header: true,
    skipEmptyLines: true
  });

  return parsed.data.filter((row) => row.Ticker && row.Company);
}

export function getUniverseStats() {
  const companies = loadCompanyUniverse();
  const industries = new Set(
    companies.map((company) => company.Industry).filter(Boolean)
  );
  const sectors = new Set(
    companies.map((company) => company.Sector).filter(Boolean)
  );

  return {
    companyCount: companies.length,
    industryCount: industries.size,
    sectorCount: sectors.size
  };
}
