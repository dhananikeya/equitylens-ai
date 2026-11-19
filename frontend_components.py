"""Streamlit Components v2 bridge for EquityLens research shortcuts.

The optional frontend preserves native Streamlit buttons on older deployments.
"""
from pathlib import Path

import streamlit as st

_ASSETS = Path(__file__).resolve().parent / "frontend"


def supports_research_actions():
    """Check feature support without invoking or registering a component."""
    return callable(getattr(getattr(st.components, "v2", None), "component", None))


@st.cache_resource(show_spinner=False)
def _research_actions_component():
    """Register exactly once per process to avoid duplicate component warnings."""
    if not supports_research_actions():
        raise RuntimeError("Streamlit Components v2 is unavailable")

    return st.components.v2.component(
        "equitylens_research_actions",
        html='<div class="el-action-grid" role="group" aria-label="Explore EquityLens"></div>',
        css=(_ASSETS / "research_actions.css").read_text(encoding="utf-8"),
        js=(_ASSETS / "research_actions.js").read_text(encoding="utf-8"),
    )


def render_research_actions(actions):
    """Render interactive cards and return the clicked destination, if any.

    Call only when supports_research_actions() returns True. Native Streamlit
    buttons remain the caller's fallback on incompatible installations.
    """
    component = _research_actions_component()
    result = component(
        key="research_action_cards_v2",
        data={"actions": [
            {"label": label, "destination": destination, "description": description}
            for label, destination, description in actions
        ]},
        on_destination_change=lambda: None,
    )
    return getattr(result, "destination", None)
