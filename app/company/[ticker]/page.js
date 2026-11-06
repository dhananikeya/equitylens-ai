import { notFound } from "next/navigation";
import { loadCompanyUniverse } from "@/lib/companies";
import { loadCompanyResearch } from "@/lib/research";
import CompanyResearch from "@/components/CompanyResearch";

export const dynamicParams = false;

export function generateStaticParams() {
  return loadCompanyUniverse().map((company) => ({
    ticker: company.ticker,
  }));
}

export async function generateMetadata({ params }) {
  const { ticker } = await params;
  const normalized = String(ticker || "").toUpperCase();
  const company = loadCompanyUniverse().find((item) => item.ticker === normalized);

  if (!company) return { title: "Company Research · EquityLens AI" };

  return {
    title: normalized + " · " + company.company + " · EquityLens AI",
    description:
      "SEC-linked financial, business, risk, and registration-filing research for " +
      company.company +
      ".",
  };
}

export default async function CompanyPage({ params }) {
  const { ticker } = await params;
  const normalized = String(ticker || "").toUpperCase();
  const companies = loadCompanyUniverse();
  const company = companies.find((item) => item.ticker === normalized);

  if (!company) notFound();

  const research = loadCompanyResearch(normalized);

  return (
    <CompanyResearch
      company={company}
      research={research}
      companies={companies}
    />
  );
}
