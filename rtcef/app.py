import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="CallBreach",
    page_icon="🛡️",
    layout="centered"
)

# =======================
# UI
# =======================
st.markdown("""
<style>
body { background:#0b0f17; color:#e6edf3; }
.card {
  background:#0f1629;
  border:1px solid #1f2a44;
  border-radius:18px;
  padding:1.6rem;
  margin-bottom:1rem;
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
.score { font-size:3.2rem; font-weight:900; }
.muted { color:#9aa4b2; font-size:.85rem; }
pre { background:#020617; padding:1rem; border-radius:12px; }
button { cursor:pointer; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 🛡️ CallBreach")
st.caption("Real‑time communication visibility assessment")
st.markdown(
    "<div class='muted'>Runs entirely in your browser. No data is transmitted, stored or shared.</div>",
    unsafe_allow_html=True
)

# =======================
# CLIENT‑SIDE ENGINE
# =======================
components.html(
"""
<!DOCTYPE html>
<html>
<body style="background:#0f1629;color:#e6edf3;font-family:system-ui">

<div id="card" class="card">
  <span class="badge idle">READY</span>
  <div class="score">— / 100</div>
  <div class="muted">Visibility score</div>
  <button onclick="runScan()" style="
    margin-top:1rem;
    padding:.6rem 1.2rem;
    border-radius:12px;
    border:none;
    background:#2563eb;
    color:white;
    font-weight:600;">
    ▶ Start deep scan
  </button>
</div>

<div id="details" class="card" style="display:none">
  <strong>Exposure analysis</strong>
  <p id="verdictText"></p>
  <pre id="jsonOut"></pre>
</div>

<script>
async function runScan() {

  document.getElementById("card").innerHTML = `
    <span class="badge mod">SCANNING…</span>
    <div class="score">— / 100</div>
    <div class="muted">Analyzing communication surface…</div>
  `;

  const R = {
    network:{},
    media:{},
    device:{},
    timing:{},
    correlation:{}
  };

  // =======================
  // NETWORK / WEBRTC
  // =======================
  R.network = {
    hasTURN:false,
    hasSRFLX:false,
    hasHOST:false,
    ipv6:false,
    mdns:false,
    interfaces:[],
    iceOrder:[],
    iceCount:0
  };

  const pc = new RTCPeerConnection({
    iceServers:[{urls:"stun:stun.l.google.com:19302"}]
  });

  pc.createDataChannel("cb");

  const t0 = performance.now();

  pc.onicecandidate = e => {
    if (!e || !e.candidate) return;
    const c = e.candidate.candidate;
    R.network.iceCount++;
    R.network.iceOrder.push({
      candidate:c,
      t:Math.round(performance.now()-t0)
    });

    if (c.includes(" typ relay ")) R.network.hasTURN = true;
    if (c.includes(" typ srflx ")) R.network.hasSRFLX = true;
    if (c.includes(" typ host ")) R.network.hasHOST = true;
    if (c.includes(".local")) R.network.mdns = true;
    if (c.toLowerCase().includes("ip6")) R.network.ipv6 = true;

    const ip = c.match(/([0-9]{1,3}(\\.[0-9]{1,3}){3})/);
    if (ip) {
      const v = ip[1];
      if (v.startsWith("10.") || v.startsWith("192.168.") || v.startsWith("172.")) {
        if (!R.network.interfaces.includes("LAN")) R.network.interfaces.push("LAN");
      } else {
        if (!R.network.interfaces.includes("PUBLIC")) R.network.interfaces.push("PUBLIC");
      }
    }
  };

  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);
  await new Promise(r=>setTimeout(r,2500));
  pc.close();

  // =======================
  // MEDIA CAPABILITIES
  // =======================
  try {
    R.media.audio = RTCRtpSender.getCapabilities("audio");
    R.media.video = RTCRtpSender.getCapabilities("video");
  } catch {
    R.media.error = "Not supported";
  }

  // =======================
  // DEVICE CONTEXT
  // =======================
  R.device = {
    cores:navigator.hardwareConcurrency || null,
    memory:navigator.deviceMemory || null,
    pixelRatio:window.devicePixelRatio,
    colorDepth:screen.colorDepth,
    touch:navigator.maxTouchPoints,
    timezone:new Date().getTimezoneOffset()
  };

  // =======================
  // TIMING / JITTER
  // =======================
  let drift=[];
  let t=performance.now();
  for(let i=0;i<5;i++){
    await new Promise(r=>setTimeout(r,50));
    drift.push(Math.round(performance.now()-t));
    t=performance.now();
  }
  R.timing.timerDrift=drift;

  // =======================
  // SCORING ENGINE
  // =======================
  let score=100;
  if(R.network.hasHOST) score-=15;
  if(R.network.hasSRFLX) score-=20;
  if(!R.network.hasTURN) score-=15;
  if(R.network.interfaces.includes("PUBLIC")) score-=20;
  if(R.network.interfaces.includes("LAN")) score-=10;
  if(R.network.interfaces.length>1) score-=10;
  if(R.network.ipv6) score-=10;
  if(!R.network.mdns) score-=5;
  if(R.network.iceCount>6) score-=5;
  if(R.device.cores && R.device.cores>8) score-=5;
  score=Math.max(score,0);

  let cls="low";
  let verdict="Low visibility — limited exposure";
  if(score<75){cls="mod"; verdict="Moderate visibility — partial exposure";}
  if(score<45){cls="high"; verdict="High visibility — strong exposure";}

  // =======================
  // RENDER
  // =======================
  document.getElementById("card").innerHTML = `
    <span class="badge ${cls}">${verdict}</span>
    <div class="score">${score}/100</div>
    <div class="muted">Global Visibility Index</div>
  `;

  document.getElementById("details").style.display="block";
  document.getElementById("verdictText").textContent = verdict;
  document.getElementById("jsonOut").textContent = JSON.stringify(R,null,2);
}
</script>

</body>
</html>
""",
height=900
)

st.divider()
st.caption("Passive • client‑side • owner‑controlled • ethical by design")
