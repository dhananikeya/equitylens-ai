import { loadCompanyUniverse } from "@/lib/companies";
import EquityLensShell from "@/components/EquityLensShell";

export default function HomePage() {
  const companies = loadCompanyUniverse();
  const industries = new Set(companies.map((company) => company.industry).filter(Boolean));

  return (
    <EquityLensShell
      companies={companies}
      industryCount={industries.size}
    />
  );
}
