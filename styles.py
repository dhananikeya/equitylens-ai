from pathlib import Path


STYLE_PATH = (
    Path(__file__).resolve().parent
    / "assets"
    / "equitylens.css"
)


def inject_global_styles(st):
    css = STYLE_PATH.read_text(
        encoding="utf-8"
    )
    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )
