import LearnLibrary, { type LearnItem } from "@/components/learn-library";

const items: LearnItem[] = [
  {
    term:"10-K", category:"SEC filings",
    definition:"A 10-K is the detailed annual report most U.S. public companies file with the SEC.",
    why:"It is one of the strongest primary sources for audited annual financials, business description, risk factors, management discussion, debt, stock compensation, and accounting notes.",
    how:"Start with Business, Risk Factors, MD&A, Financial Statements, and Notes. Then compare the annual picture with newer 10-Q and 8-K filings.",
    watch:"A 10-K is comprehensive but backward-looking, so do not treat it as the newest available picture.",
    sourceUrl:"https://www.sec.gov/submit-filings/forms-index"
  },
  {
    term:"10-Q", category:"SEC filings",
    definition:"A 10-Q is the quarterly report most U.S. public companies file for the first three fiscal quarters.",
    why:"It provides newer financial statements and management commentary between annual 10-K filings.",
    how:"Compare the newest quarter with the same quarter a year earlier and read the notes for balance-sheet, cash-flow, and accounting changes.",
    watch:"Quarterly results can be seasonal or volatile, so one quarter should not be treated as a long-term trend.",
    sourceUrl:"https://www.sec.gov/submit-filings/forms-index"
  },
  {
    term:"8-K", category:"SEC filings",
    definition:"Form 8-K is a current report used to disclose specified significant corporate events between periodic reports.",
    why:"It can surface material agreements, acquisitions, leadership changes, financing events, earnings-related disclosures, and other important developments.",
    how:"Read the item number, event date, exhibits, and any attached press release or agreement.",
    watch:"Some information may be furnished rather than filed, and not every company announcement requires an 8-K.",
    sourceUrl:"https://www.sec.gov/submit-filings/forms-index"
  },
  {
    term:"S-1 Registration Statement", category:"SEC filings",
    definition:"Form S-1 is the SEC registration statement commonly associated with U.S. companies registering securities for an IPO.",
    why:"It can offer the first detailed public view of a company's business model, historical financials, risks, ownership, management, and proposed use of proceeds.",
    how:"Start with the Prospectus Summary, Risk Factors, Use of Proceeds, MD&A, Business, Financial Statements, and Principal Stockholders.",
    watch:"Offering terms can change through S-1/A amendments, and filing an S-1 does not guarantee an IPO will be completed.",
    sourceUrl:"https://www.sec.gov/submit-filings/forms-index"
  },
  {
    term:"Revenue", category:"Financials",
    definition:"Revenue is the money a company earns from selling products or services before expenses are deducted.",
    why:"It helps show the scale of the business and whether demand is expanding, slowing, or shrinking.",
    how:"Compare revenue across the same quarter year over year and across multiple fiscal years.",
    watch:"Revenue growth alone does not tell you whether the company is profitable or generating cash."
  },
  {
    term:"Year-over-Year Growth", category:"Financials",
    definition:"Year-over-year growth measures how much a metric changed versus the same period one year earlier.",
    why:"Comparing the same period across years reduces many seasonal distortions.",
    how:"Formula: (current period minus prior-year period) divided by prior-year period, multiplied by 100.",
    watch:"Check whether growth is accelerating or slowing and whether margins improve alongside it."
  },
  {
    term:"Gross Margin", category:"Financials",
    definition:"Gross margin is the percentage of revenue left after the direct costs required to deliver the product or service.",
    why:"It provides a basic view of product economics and how much revenue remains to fund operating expenses.",
    how:"Formula: gross profit divided by revenue multiplied by 100.",
    watch:"Margin structures vary widely by industry, so compare with the company's own history and close peers."
  },
  {
    term:"Operating Margin", category:"Financials",
    definition:"Operating margin shows operating profit or loss after core operating expenses.",
    why:"It helps show whether the core business is becoming more efficient as it grows.",
    how:"Formula: operating income divided by revenue multiplied by 100.",
    watch:"A single quarter may be distorted by restructuring, launch costs, acquisitions, or unusual spending."
  },
  {
    term:"Net Income", category:"Financials",
    definition:"Net income is the final reported profit or loss after operating expenses, interest, taxes, and other gains or losses.",
    why:"It is the bottom line, but it can differ meaningfully from core operating performance.",
    how:"Read it alongside operating income, cash flow, taxes, interest, and unusual gains or charges.",
    watch:"One-time tax benefits, investment gains, or restructuring charges can make a single period less representative."
  },
  {
    term:"LTM / Trailing Twelve Months", category:"Financials",
    definition:"LTM combines the most recent twelve months of results, usually using the latest four reported quarters.",
    why:"It gives a more current full-year view than an older annual report when newer quarters have already been filed.",
    how:"Combine the latest four quarters or reconcile the latest annual result with subsequent quarters.",
    watch:"LTM is calculated, not a separate SEC reporting period, so always verify which periods are included."
  },
  {
    term:"Consumer Price Index (CPI)", category:"Macro",
    definition:"CPI measures the average change over time in prices paid by urban consumers for a basket of goods and services.",
    why:"It is a widely watched U.S. inflation measure that can affect interest-rate expectations, borrowing costs, and valuation assumptions.",
    how:"Compare the latest index level with the level twelve months earlier for year-over-year inflation. Core CPI excludes food and energy.",
    watch:"Distinguish monthly from year-over-year changes and headline CPI from core CPI and PCE.",
    sourceUrl:"https://www.bls.gov/cpi/"
  },
  {
    term:"Employment Situation", category:"Macro",
    definition:"The BLS Employment Situation combines payroll employment, unemployment, participation, and earnings data.",
    why:"Labor-market strength influences household income, demand, inflation pressure, and expectations for monetary policy.",
    how:"Common focal points are payroll growth, the unemployment rate, labor-force participation, and average hourly earnings.",
    watch:"Payroll estimates can be revised, and the household and payroll surveys can diverge in a given month.",
    sourceUrl:"https://www.bls.gov/news.release/empsit.htm"
  },
  {
    term:"JOLTS", category:"Macro",
    definition:"JOLTS reports job openings, hires, quits, layoffs, and other labor-turnover measures.",
    why:"It helps show labor demand and worker confidence beyond the monthly payroll count.",
    how:"Watch job openings, the quits rate, and the balance between openings and unemployed workers.",
    watch:"JOLTS is released with a lag and can be revised.",
    sourceUrl:"https://www.bls.gov/jlt/"
  },
  {
    term:"10-Year Treasury Yield", category:"Rates",
    definition:"The 10-year Treasury yield is the market yield around the 10-year point on the U.S. Treasury par yield curve.",
    why:"It is a widely watched benchmark for long-term rates, discount rates, mortgages, and borrowing costs.",
    how:"Compare it with shorter maturities to understand curve shape and changes in rate expectations.",
    watch:"Treasury yields reflect inflation, real rates, policy expectations, growth, supply and demand, and risk sentiment.",
    sourceUrl:"https://home.treasury.gov/resource-center/data-chart-center/interest-rates"
  },
  {
    term:"SOFR", category:"Rates",
    definition:"SOFR is a broad measure of overnight borrowing costs collateralized by U.S. Treasury securities.",
    why:"It is a central reference rate for U.S. dollar floating-rate financing and derivatives after LIBOR.",
    how:"Use the daily rate and the New York Fed's compounded averages for context on short-term financing conditions.",
    watch:"SOFR itself is an overnight secured rate. Term rates and swap rates are different market measures.",
    sourceUrl:"https://www.newyorkfed.org/markets/reference-rates/sofr"
  }
];

export default function LearnPage() {
  const categories = new Set(items.map((item) => item.category));
  return (
    <main className="shell learn-page">
      <section className="research-intro learn-intro">
        <p className="eyebrow">LEARN</p>
        <h1>Understand the numbers <span>before trusting the narrative.</span></h1>
        <p className="lede">
          Plain-language explanations of filings, financial metrics, rates, and macro indicators,
          with practical guidance on what each measure tells you and what it does not.
        </p>
        <div className="learn-stats">
          <div><strong>{items.length}</strong><span>concepts</span></div>
          <div><strong>{categories.size}</strong><span>learning categories</span></div>
        </div>
      </section>

      <LearnLibrary items={items} />

      <section className="methodology-note">
        <strong>Education, not investment advice.</strong>
        <p>
          EquityLens explains public-company and market concepts for research and learning.
          Source links are provided where a primary public reference is available.
        </p>
      </section>
    </main>
  );
}
