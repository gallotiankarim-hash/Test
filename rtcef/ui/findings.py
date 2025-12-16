import streamlit as st

def render_findings(findings):
    for f in findings:
        st.json(f)