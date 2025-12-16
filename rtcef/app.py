import streamlit as st
import yaml
from pathlib import Path
from streamlit_javascript import st_javascript

# ==================================================
# LOAD POLICY
# ==================================================
policy = yaml.safe_load(Path("policy.yaml").read_text())

FEATURES = policy["features"]
SIMULATION = policy["simulation"]
UI = policy["ui"]

# ==================================================
# PAGE
# ==================================================
st.set_page_config(
    page_title=policy["app"]["name"],
    page_icon="🛡️",
    layout="centered"
)

# ==================================================
# SESSION STATE
# ==================================================
st.session_state.setdefault("scan_requested", False)
st.session_state.setdefault("scan_done", False)
st.session_state.setdefault("signals", None)

# ==================================================
# STYLE
# ==================================================
st.markdown("""
<style>
body { background:#0b0f17; color:#e6edf3; }
.card {
  background:#0f1629;
  border:1px solid #1f2a44;
  border-radius:18px;
  padding:1.8rem;
}
.badge {
  padding:.35rem .9rem;
  border-radius:999px;
  font-size:.75rem;
  font-weight:700;
}
.low { background:#064e3b; color:#6ee7b7; }
.mod { background:#78350f; color:#fde68a; }
.high{ background:#7f1d1d; color:#fecaca; }
.idle{ background:#1f2937; color:#9ca3af; }
.score { font-size:3rem; font-weight:900; }
.muted { color:#9aa4b2; font-size:.85rem; }
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================
st.markdown(f"## 🛡️ {policy['app']['name']}")
st.caption("Real‑time communication visibility assessment")
st.divider()

# ==================================================
# BUTTON
# ==================================================
if st.button("🔎 Run visibility scan"):
    st.session_state.scan_requested = True
    st.session_state.scan_done = False
    st.session_state.signals = None

# ==================================================
# JAVASCRIPT SCAN (NON BLOCKING)
# ==================================================
if st.session_state.scan_requested and not st.session_state.scan_done:

    st.info("Scanning communication visibility…")

    js_result = st_javascript(
        """
        async () => {
          const r = {
            hasTURN:false,
            hasSRFLX:false,
            hasHOST:false,
            ipv6:false,
            mdns:false,
            interfaces:[]
          };

          const pc = new RTCPeerConnection({
            iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
          });

          pc.createDataChannel("cb");

          pc.onicecandidate = e => {
            if (!e || !e.candidate) return;
            const c = e.candidate.candidate;

            if (c.includes(" typ relay ")) r.hasTURN = true;
            if (c.includes(" typ srflx ")) r.hasSRFLX = true;
            if (c.includes(" typ host ")) r.hasHOST = true;
            if (c.includes(".local")) r.mdns = true;
            if (c.toLowerCase().includes("ip6")) r.ipv6 = true;

            const ip = c.match(/([0-9]{1,3}(\\.[0-9]{1,3}){3})/);
            if (ip) {
              const v = ip[1];
              if (
                v.startsWith("10.") ||
                v.startsWith("192.168.") ||
                v.startsWith("172.")
              ) {
                if (!r.interfaces.includes("LAN")) r.interfaces.push("LAN");
              } else {
                if (!r.interfaces.includes("PUBLIC")) r.interfaces.push("PUBLIC");
              }
            }
          };

          const offer = await pc.createOffer();
          await pc.setLocalDescription(offer);
          await new Promise(r => setTimeout(r, 2500));
          pc.close();
          return r;
        }
        """,
        key="scan_js"
    )

    # IMPORTANT: accept result when it arrives (even next rerun)
    if js_result is not None:
        st.session_state.signals = js_result
        st.session_state.scan_done = True

# ==================================================
# SCORE
# ==================================================
signals = st.session_state.signals

if st.session_state.scan_done and signals:
    score = 100
    if signals.get("hasHOST"): score -= 15
    if signals.get("hasSRFLX"): score -= 20
    if not signals.get("hasTURN"): score -= 15
    if "PUBLIC" in signals.get("interfaces", []): score -= 20
    if "LAN" in signals.get("interfaces", []): score -= 10
    if len(signals.get("interfaces", [])) > 1: score -= 10
    if signals.get("ipv6"): score -= 10
    if not signals.get("mdns"): score -= 5
    score = max(score, 0)

    if score >= 75:
        verdict, cls = "LOW VISIBILITY", "low"
    elif score >= 45:
        verdict, cls = "MODERATE VISIBILITY", "mod"
    else:
        verdict, cls = "HIGH VISIBILITY", "high"

elif st.session_state.scan_requested:
    verdict, cls, score = "SCANNING…", "mod", None
else:
    verdict, cls, score = "NO SCAN RUN", "idle", None

# ==================================================
# UI
# ==================================================
st.markdown(f"""
<div class="card">
  <span class="badge {cls}">{verdict}</span>
  <div class="score">
    {"— / 100" if score is None else f"{score}/100"}
  </div>
  <div class="muted">Visibility score (policy‑driven)</div>
</div>
""", unsafe_allow_html=True)

if UI["show_technical_details"] and signals:
    with st.expander("🔍 Technical signals"):
        st.json(signals)

st.caption(
    "Behavior controlled by policy.yaml — passive, client‑side, ethical by design."
)
