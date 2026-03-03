import pathlib
import streamlit as st

# Adjust if home.py is elsewhere
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
readme_path = PROJECT_ROOT / "README.md"

readme_text = readme_path.read_text(encoding="utf-8")

# Option 1: render whole README
st.markdown(readme_text, unsafe_allow_html=False)