from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence


@dataclass(frozen=True)
class CompanyIdentifier:
    ticker: str
    cik: str = ""
    name: str = ""

    @property
    def normalized_ticker(self) -> str:
        return self.ticker.upper().strip()

    @property
    def normalized_cik(self) -> str:
        digits = "".join(
            character
            for character in str(self.cik)
            if character.isdigit()
        )
        return digits.zfill(10) if digits else ""


@dataclass
class CompanyResearchContext:
    workspace_universe: Any
    company_data: Mapping[str, dict]
    company_analysis: Mapping[str, dict]
    company_quarterly: Mapping[str, dict]
    company_s1: Mapping[str, dict]
    analysis_by_ticker: Mapping[str, dict]
    quarterly_by_ticker: Mapping[str, dict]
    s1_by_ticker: Mapping[str, dict]
    industries: Sequence[str]
    load_sec_company: Callable[..., dict]
    open_company_research: Callable[..., Any]
    reset_coverage_selection: Callable[..., Any]
    remember_choice: Callable[..., Any]
    clear_company_filters: Callable[..., Any]
    compare_company: Callable[..., Any]
    retry_company_data: Callable[..., Any]
    research_link: Callable[..., str]
    save_rendered_choices: Callable[..., Any]
    navigate_to: Callable[..., Any]


@dataclass
class IndustryComparisonContext:
    industries: Sequence[str]
    company_data: Mapping[str, dict]
    subgroups: Mapping[str, Any]
    public_market_data_enabled: bool
    company_quarterly: Mapping[str, dict]
    analysis_by_ticker: Mapping[str, dict]
    company_analysis: Mapping[str, dict]
    remember_choice: Callable[..., Any]
    company_universe: Any
    research_link: Callable[..., str]
