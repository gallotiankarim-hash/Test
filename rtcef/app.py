import streamlit as st
import json
import yaml
import streamlit.components.v1 as components
from pathlib import Path

# ==================================================
# LOAD POLICY (SINGLE SOURCE OF TRUTH)
# ==================================================
POLICY_FILE = Path("policy.yaml")

if not POLICY_FILE.exists():
    st.error("policy.yaml not found — application halted")
    st.stop()

policy = yaml.safe_load(POLICY_FILE.read_text())

APP_MODE = policy["app"]["mode"]
ETHICS = policy["ethics"]
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
.card { background:#0f1629; border:1px solid #1f2a44; border-radius:16px;
        padding:1.6rem; margin-bottom:1.2rem; }
.badge { padding:.35rem .8rem; border-radius:999px;
         font-size:.72rem; font-weight:700; letter-spacing:.05em; }
.low { background:#064e3b; color:#6ee7b7; }
.mod { background:#78350f; color:#fde68a; }
.high{ background:#7f1d1d; color:#fecaca; }
.muted { color:#9aa4b2; font-size:.85rem; }
.score { font-size:3rem; font-weight:900; }
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================
st.markdown(f"## 🛡️ {policy['app']['name']}")
st.markdown("<div class='muted'>Real‑time communication visibility assessment</div>", unsafe_allow_html=True)
st.divider()

# ==================================================
# SIGNAL COLLECTION (TRUE MODE ONLY)
# ==================================================
signals = {}

if APP_MODE == "true" and FEATURES["webrtc"]["enabled"]:
    js = """
    <script>
    (async () => {
      const s = {
        ips: new Set(),
        hasTURN:false, hasSRFLX:false, hasHOST:false,
        mdns:false, ipv6:false, interfaces:new Set()
      };
      const pc = new RTCPeerConnection({iceServers:[{urls:"stun:stun.l.google.com:19302"}]});
      pc.createDataChannel("x");
      pc.onicecandidate = e => {
        if (!e || !e.candidate) {
          window.parent.postMessage(JSON.stringify({
            ips:[...s.ips], hasTURN:s.hasTURN, hasSRFLX:s.hasSRFLX,
            hasHOST:s.hasHOST, mdns:s.mdns, ipv6:s.ipv6,
            interfaces:[...s.interfaces]
          }),"*");
          return;
        }
        const c=e.candidate.candidate;
        if(c.includes(" typ relay ")) s.hasTURN=true;
        if(c.includes(" typ srflx ")) s.hasSRFLX=true;
        if(c.includes(" typ host ")) s.hasHOST=true;
        if(c.includes(".local")) s.mdns=true;
        const m4=c.match(/([0-9]{1,3}(\\.[0-9]{1,3}){3})/);
        if(m4){
          s.ips.add(m4[1]);
          if(m4[1].startsWith("10.")||m4[1].startsWith("192.168.")||m4[1].startsWith("172."))
            s.interfaces.add("LAN");
          else s.interfaces.add("PUBLIC");
        }
        if(c.includes("IP6")) s.ipv6=true;
      };
      const o=await pc.createOffer(); await pc.setLocalDescription(o);
    })();
    </script>
    """
    payload = components.html(js, height=0)
    if payload:
        try:
            signals = json.loads(payload)
        except:
            signals = {}

# ==================================================
# SIMULATION MODE (ONLY IF YAML ENABLES IT)
# ==================================================
if APP_MODE == "simulation" and SIMULATION["enabled"]:
    level = SIMULATION["dataset"]
    if level == "mock_low":
        signals = {"hasTURN":True,"hasHOST":False,"hasSRFLX":False,"interfaces":[]}
    elif level == "mock_medium":
        signals = {"hasTURN":False,"hasHOST":True,"hasSRFLX":True,"interfaces":["LAN"]}
    else:
        signals = {"hasTURN":False,"hasHOST":True,"hasSRFLX":True,"interfaces":["LAN","PUBLIC"]}

# ==================================================
# SCORING (CORRELATED)
# ==================================================
score = FEATURES["scoring"]["max_score"]

if signals.get("hasHOST"): score -= 15
if signals.get("hasSRFLX"): score -= 20
if not signals.get("hasTURN"): score -= 15
if "PUBLIC" in signals.get("interfaces",[]): score -= 20
if "LAN" in signals.get("interfaces",[]): score -= 10
if len(signals.get("interfaces",[])) > 1: score -= 10

score = max(score, 0)

if score >= 75:
    verdict, cls = "LOW VISIBILITY", "low"
elif score >= 45:
    verdict, cls = "MODERATE VISIBILITY", "mod"
else:
    verdict, cls = "HIGH VISIBILITY", "high"

# ==================================================
# UI
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

# ==================================================
# FOOTER
# ==================================================
st.divider()
st.caption(
    "Behavior controlled by policy.yaml — passive, client‑side, ethical by design."
)
