import streamlit as st
import yaml
from pathlib import Path
from streamlit_javascript import st_javascript

# ==================================================
# LOAD POLICY (SINGLE SOURCE OF TRUTH)
# ==================================================
POLICY_FILE = Path("policy.yaml")

if not POLICY_FILE.exists():
    st.error("policy.yaml missing — application halted")
    st.stop()

policy = yaml.safe_load(POLICY_FILE.read_text())

APP_MODE = policy["app"]["mode"]
FEATURES = policy["features"]
SIMULATION = policy["simulation"]
UI = policy["ui"]

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title=policy["app"]["name"],
    page_icon="🛡️",
    layout="centered"
)

# ==================================================
# STYLE
# ==================================================
st.markdown("""
<style>
body { background:#0b0f17; color:#e6edf3; }
.card { background:#0f1629; border:1px solid #1f2a44;
        border-radius:18px; padding:1.8rem; margin-bottom:1.2rem; }
.badge { padding:.35rem .9rem; border-radius:999px;
         font-size:.75rem; font-weight:700; letter-spacing:.05em; }
.low { background:#064e3b; color:#6ee7b7; }
.mod { background:#78350f; color:#fde68a; }
.high{ background:#7f1d1d; color:#fecaca; }
.muted { color:#9aa4b2; font-size:.85rem; }
.score { font-size:3.2rem; font-weight:900; }
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================
st.markdown(f"## 🛡️ {policy['app']['name']}")
st.markdown(
    "<div class='muted'>Real‑time communication visibility assessment</div>",
    unsafe_allow_html=True
)
st.divider()

# ==================================================
# SIGNAL COLLECTION (REAL JS → PYTHON)
# ==================================================
signals = {}

if APP_MODE == "true" and FEATURES["webrtc"]["enabled"]:

    signals = st_javascript("""
    async () => {
      const result = {
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

        if (c.includes(" typ relay ")) result.hasTURN = true;
        if (c.includes(" typ srflx ")) result.hasSRFLX = true;
        if (c.includes(" typ host ")) result.hasHOST = true;
        if (c.includes(".local")) result.mdns = true;
        if (c.includes("IP6") || c.includes("ip6")) result.ipv6 = true;

        const ipv4 = c.match(/([0-9]{1,3}(\\.[0-9]{1,3}){3})/);
        if (ipv4) {
          const ip = ipv4[1];
          if (
            ip.startsWith("10.") ||
            ip.startsWith("192.168.") ||
            ip.startsWith("172.")
          ) {
            if (!result.interfaces.includes("LAN"))
              result.interfaces.push("LAN");
          } else {
            if (!result.interfaces.includes("PUBLIC"))
              result.interfaces.push("PUBLIC");
          }
        }
      };

      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      await new Promise(resolve => setTimeout(resolve, 1500));
      pc.close();

      return result;
    }
    """)

# ==================================================
# SIMULATION (ONLY IF POLICY ENABLES IT)
# ==================================================
if SIMULATION["enabled"]:
    dataset = SIMULATION["dataset"]
    if dataset == "mock_low":
        signals = {"hasTURN":True,"hasHOST":False,"hasSRFLX":False,"interfaces":[]}
    elif dataset == "mock_medium":
        signals = {"hasTURN":False,"hasHOST":True,"hasSRFLX":True,"interfaces":["LAN"]}
    elif dataset == "mock_high":
        signals = {"hasTURN":False,"hasHOST":True,"hasSRFLX":True,"interfaces":["LAN","PUBLIC"]}

# ==================================================
# SCORING (CORRELATED, REAL)
# ==================================================
score = policy["features"]["scoring"]["max_score"]

if signals.get("hasHOST"): score -= 15
if signals.get("hasSRFLX"): score -= 20
if not signals.get("hasTURN"): score -= 15
if "PUBLIC" in signals.get("interfaces",[]): score -= 20
if "LAN" in signals.get("interfaces",[]): score -= 10
if len(signals.get("interfaces",[])) > 1: score -= 10
if signals.get("ipv6"): score -= 10
if not signals.get("mdns"): score -= 5

score = max(score, 0)

if score >= 75:
    verdict, cls = "LOW VISIBILITY", "low"
elif score >= 45:
    verdict, cls = "MODERATE VISIBILITY", "mod"
else:
    verdict, cls = "HIGH VISIBILITY", "high"

# ==================================================
# UI OUTPUT
# ==================================================
st.markdown(f"""
<div class="card">
  <span class="badge {cls}">{verdict}</span>
  <div class="score">{score}/100</div>
  <div class="muted">Visibility score (policy‑driven)</div>
</div>
""", unsafe_allow_html=True)

if UI["show_technical_details"]:
    with st.expander("🔍 Technical signals"):
        st.json(signals)

st.divider()
st.caption("Behavior controlled by policy.yaml — passive, client‑side, ethical by design.")
