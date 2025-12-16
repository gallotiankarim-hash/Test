import streamlit as st
from core.session import Session
from core.exposure import ExposureEngine
from core.scoring import score
from capture.mock import generate_mock_flows
from ui.dashboard import render_dashboard
from ui.findings import render_findings

st.title("RTCEF — Real‑Time Communication Exposure Framework")

session = Session()
engine = ExposureEngine()

flows = generate_mock_flows()
for flow in flows:
    session.add_flow(flow)
    findings = engine.analyze(flow)
    for f in findings:
        session.add_finding(f)

exposure_score = score(session.findings)

render_dashboard(session, exposure_score)
render_findings(session.findings)