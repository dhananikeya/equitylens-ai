"""Canonical EquityLens calculation definitions.

Keep formulas here aligned with the actual calculation helpers. Provider-supplied
metrics such as market cap and P/E are deliberately not described as EquityLens
calculations.
"""

CALCULATION_FORMULAS = {
    "revenue_growth": {
        "label": "Revenue growth",
        "formula": (
            "(current-period revenue − comparable prior-period revenue) "
            "÷ comparable prior-period revenue × 100"
        ),
        "requirements": (
            "Both revenue values must exist and the prior-period value must be non-zero."
        ),
    },
    "gross_margin": {
        "label": "Gross margin",
        "formula": (
            "gross profit ÷ revenue × 100"
        ),
        "requirements": (
            "Gross profit and revenue must come from the same reporting period."
        ),
    },
    "operating_margin": {
        "label": "Operating margin",
        "formula": (
            "operating income ÷ revenue × 100"
        ),
        "requirements": (
            "Operating income and revenue must come from the same reporting period."
        ),
    },
    "net_margin": {
        "label": "Net margin",
        "formula": (
            "net income ÷ revenue × 100"
        ),
        "requirements": (
            "Net income and revenue must come from the same reporting period."
        ),
    },
    "free_cash_flow": {
        "label": "Free cash flow",
        "formula": (
            "operating cash flow − capital expenditures"
        ),
        "requirements": (
            "Used only when a direct reported free-cash-flow row is unavailable. "
            "Operating cash flow and capital expenditures must refer to the same statement period."
        ),
    },
    "ltm": {
        "label": "LTM / trailing twelve months",
        "formula": (
            "sum of the latest four consecutive reported quarters"
        ),
        "requirements": (
            "All four consecutive quarter frames must exist. EquityLens does not skip a missing "
            "quarter and substitute an older one."
        ),
    },
}

DATA_TREATMENT_RULES = [
    "Missing values remain unavailable and are never replaced with zero.",
    "Reported values remain separate from EquityLens-calculated metrics.",
    "Annual and quarterly period labels come from the actual reporting period, not merely filing context.",
    "Financial-statement amounts retain their reporting currency; EquityLens does not perform FX conversion.",
    "Absolute financial amounts in different reporting currencies are not ranked against one another.",
    "SEC filing links remain the authoritative source for filing-derived facts.",
]


def calculation_methodology_markdown():
    lines = ["**EquityLens calculations**", ""]
    for item in CALCULATION_FORMULAS.values():
        lines.append(
            f"- **{item['label']}** = {item['formula']}. "
            f"{item['requirements']}"
        )
    lines.extend([
        "",
        "**Data treatment rules**",
        "",
    ])
    lines.extend(
        f"- {rule}"
        for rule in DATA_TREATMENT_RULES
    )
    return "\n".join(lines)
