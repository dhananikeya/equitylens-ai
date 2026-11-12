import CompanySearch from "@/components/company-search";
import { getResearchDirectory } from "@/lib/research-data";

export default function CompanyResearchIndexPage() {
  const companies = getResearchDirectory();

  return (
    <main className="shell research-index">
      <section className="research-intro">
        <p className="eyebrow">COMPANY RESEARCH</p>
        <h1>Start with the company. <span>Verify with the filing.</span></h1>
        <p className="lede">
          Search the full EquityLens universe by company name or ticker. Each research page
          separates reported financial facts, calculated metrics, structured research context,
          and original-source evidence.
        </p>
      </section>
      <CompanySearch companies={companies} />
      <p className="directory-note">{companies.length.toLocaleString("en-US")} companies available in the research directory.</p>
    </main>
  );
}
