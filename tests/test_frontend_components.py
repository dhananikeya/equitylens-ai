"""Focused checks for the optional frontend bridge (no Streamlit server needed)."""
import functools
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "frontend_components.py"


def load_bridge(v2_enabled=True):
    calls = []
    component_calls = []

    def component_factory(name, **kwargs):
        calls.append((name, kwargs))

        def mount(**kwargs):
            component_calls.append(kwargs)
            return types.SimpleNamespace(destination="Company Research")

        return mount

    fake_components = types.SimpleNamespace(
        v2=types.SimpleNamespace(component=component_factory) if v2_enabled else None
    )
    fake_streamlit = types.SimpleNamespace(
        components=fake_components,
        cache_resource=lambda **kwargs: functools.lru_cache(maxsize=None),
    )
    spec = importlib.util.spec_from_file_location("equitylens_frontend_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {"streamlit": fake_streamlit}):
        spec.loader.exec_module(module)
    return module, calls, component_calls


class FrontendComponentTests(unittest.TestCase):
    def test_legacy_streamlit_uses_native_fallback(self):
        bridge, _, _ = load_bridge(v2_enabled=False)
        self.assertFalse(bridge.supports_research_actions())

    def test_destination_and_registration(self):
        bridge, registrations, mounts = load_bridge()
        self.assertTrue(bridge.supports_research_actions())
        actions = [("Research a company", "Company Research", "SEC filing research")]
        self.assertEqual(bridge.render_research_actions(actions), "Company Research")
        self.assertEqual(bridge.render_research_actions(actions), "Company Research")
        self.assertEqual(len(registrations), 1, "register component once")
        self.assertEqual(mounts[0]["data"]["actions"][0]["destination"], "Company Research")
        self.assertTrue(callable(mounts[0]["on_destination_change"]))

    def test_assets_are_present_and_safe_text_rendering(self):
        js = (ROOT / "frontend" / "research_actions.js").read_text(encoding="utf-8")
        css = (ROOT / "frontend" / "research_actions.css").read_text(encoding="utf-8")
        self.assertIn("textContent", js)
        self.assertNotIn("innerHTML", js)
        self.assertIn("setTriggerValue", js)
        self.assertIn("focus-visible", css)
        self.assertIn("prefers-reduced-motion", css)


if __name__ == "__main__":
    unittest.main()
