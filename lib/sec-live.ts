export type SecResearchFiling = {
  form: string;
  filingDate: string;
  reportDate: string;
  description: string;
  items: string;
  accessionNumber: string;
  url: string;
};

const RESEARCH_FORMS = new Set([
  "10-K", "10-K/A",
  "10-Q", "10-Q/A",
  "8-K", "8-K/A",
  "20-F", "20-F/A",
  "40-F", "40-F/A",
  "6-K", "6-K/A",
  "S-1", "S-1/A",
  "F-1", "F-1/A",
  "S-11", "S-11/A",
  "424B1", "424B2", "424B3", "424B4", "424B5",
  "DEF 14A", "DEFA14A"
]);

function secUrl(cik: string, accession: string, primaryDocument: string) {
  if (!cik || !accession || !primaryDocument) return "";
  return (
    "https://www.sec.gov/Archives/edgar/data/" +
    String(Number(cik)) +
    "/" +
    accession.replace(/-/g, "") +
    "/" +
    primaryDocument
  );
}

export async function getSecResearchFilings(cikInput: string | null | undefined) {
  const cik = String(cikInput || "").replace(/\D/g, "").padStart(10, "0");
  if (!/^\d{10}$/.test(cik) || cik === "0000000000") return [];

  try {
    const response = await fetch(
      `https://data.sec.gov/submissions/CIK${cik}.json`,
      {
        headers: {
          "User-Agent": "EquityLens AI research app dhananikeya@gmail.com",
          "From": "dhananikeya@gmail.com",
          "Accept": "application/json"
        },
        next: { revalidate: 900 }
      }
    );

    if (!response.ok) return [];
    const payload = await response.json();
    const recent = payload?.filings?.recent || {};
    const forms: string[] = Array.isArray(recent.form) ? recent.form : [];

    const value = (field: string, index: number) => {
      const values = Array.isArray(recent?.[field]) ? recent[field] : [];
      return String(values[index] ?? "");
    };

    return forms
      .map((form, index): SecResearchFiling => {
        const accessionNumber = value("accessionNumber", index);
        const primaryDocument = value("primaryDocument", index);
        return {
          form,
          filingDate: value("filingDate", index),
          reportDate: value("reportDate", index),
          description:
            value("primaryDocDescription", index) || primaryDocument,
          items: value("items", index),
          accessionNumber,
          url: secUrl(cik, accessionNumber, primaryDocument)
        };
      })
      .filter((filing) => RESEARCH_FORMS.has(filing.form))
      .slice(0, 12);
  } catch {
    return [];
  }
}
