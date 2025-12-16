import streamlit as st
import yaml
from pathlib import Path
import streamlit.components.v1 as components

# ==================================================
# LOAD POLICY
# ==================================================
policy = yaml.safe_load(Path("policy.yaml").read_text())

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

st.markdown("""
<div class="muted">
This assessment runs entirely in your browser.
No data is transmitted, stored or shared.
</div>
""", unsafe_allow_html=True)

# ==================================================
# CLIENT‑SIDE WEBRTC SCAN (REAL)
# ==================================================
components.html(
"""
<!DOCTYPE html>
<html>
<body style="background:#0f1629;color:#e6edf3;font-family:system-ui">

<div id="result" class="card">
  <span class="badge idle">READY</span>
  <div class="score">— / 100</div>
  <div class="muted">Click start to run scan</div>
  <button onclick="runScan()" style="
    margin-top:1rem;
    padding:.6rem 1.2rem;
    border-radius:12px;
    border:none;
    background:#2563eb;
    color:white;
    font-weight:600;
    cursor:pointer;">
    ▶ Start visibility scan
  </button>
</div>

<script>
async function runScan() {

  document.getElementById("result").innerHTML = `
    <span class="badge mod">SCANNING…</span>
    <div class="score">— / 100</div>
    <div class="muted">Analyzing WebRTC exposure…</div>
  `;

  const r = {
    hasTURN:false,
    hasSRFLX:false,
    hasHOST:false,
    ipv6:false,
    mdns:false,
    interfaces:[]
  };

  const pc = new RTCPeerConnection({
    iceServers:[{urls:"stun:stun.l.google.com:19302"}]
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

  let score = 100;
  if (r.hasHOST) score -= 15;
  if (r.hasSRFLX) score -= 20;
  if (!r.hasTURN) score -= 15;
  if (r.interfaces.includes("PUBLIC")) score -= 20;
  if (r.interfaces.includes("LAN")) score -= 10;
  if (r.interfaces.length > 1) score -= 10;
  if (r.ipv6) score -= 10;
  if (!r.mdns) score -= 5;
  score = Math.max(score,0);

  let verdict="LOW VISIBILITY", cls="low";
  if (score < 75) { verdict="MODERATE VISIBILITY"; cls="mod"; }
  if (score < 45) { verdict="HIGH VISIBILITY"; cls="high"; }

  document.getElementById("result").innerHTML = `
    <span class="badge ${cls}">${verdict}</span>
    <div class="score">${score}/100</div>
    <pre style="margin-top:1rem">${JSON.stringify(r,null,2)}</pre>
  `;
}
</script>

<style>
.card {
  border:1px solid #1f2a44;
  border-radius:18px;
  padding:1.6rem;
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

</body>
</html>
""",
height=600
)

st.divider()
st.caption(
    "Passive, client‑side, ethical by design — no identification, no tracking."
)
