"""Small, optional Streamlit Components v2 frontend layer for EquityLens."""
from pathlib import Path

import streamlit as st

_ASSETS = Path(__file__).resolve().parent / "frontend"


def render_research_actions(actions):
    """Return selected destination, or None when nothing was selected.

    Requires Streamlit Components v2 (Streamlit >= 1.51). Returns None when
    unavailable so callers can preserve native Streamlit controls as fallback.
    """
    v2 = getattr(st.components, "v2", None)
    if v2 is None or not hasattr(v2, "component"):
        raise RuntimeError("Streamlit Components v2 is unavailable")

    component = v2.component(
        "equitylens_research_actions",
        html='<div class="el-action-grid" role="group" aria-label="Explore EquityLens"></div>',
        css=(_ASSETS / "research_actions.css").read_text(encoding="utf-8"),
        js=(_ASSETS / "research_actions.js").read_text(encoding="utf-8"),
    )
    result = component(
        key="research_action_cards_v2",
        data={"actions": [
            {"label": label, "destination": destination, "description": description}
            for label, destination, description in actions
        ]},
    )
    return getattr(result, "destination", None)
