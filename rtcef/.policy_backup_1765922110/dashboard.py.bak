import streamlit as st

def render_dashboard(session, score):
    st.metric("Peers", len(session.peers))
    st.metric("Flows", len(session.flows))
    st.metric("Exposure Score", score)