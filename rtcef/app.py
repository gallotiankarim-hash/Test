import streamlit as st
import streamlit.components.v1 as components

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(
    page_title="CallBreach",
    page_icon="🛡️",
    layout="centered"
)

# ======================
# LANG STRINGS
# ======================
LANG = {
    "EN": {
        "title": "Real‑time communication visibility assessment",
        "subtitle": "Runs entirely in your browser. No data is transmitted, stored or shared.",
        "start": "Start deep scan",
        "score": "Visibility score",
        "risk": "Surveillance risk indicators",
        "logs": "Scan logs",
        "ethical": "Passive • client‑side • owner‑controlled • ethical by design",
        "explain_title": "What does this mean?",
        "explain_body": (
            "This assessment does not prove surveillance. It identifies technical conditions "
            "compatible with monitoring or sensitive environments (e.g., audio permissions, "
            "WebRTC exposure, abnormal timing). Results are indicators, not confirmation."
        )
    },
    "FR": {
        "title": "Évaluation de la visibilité des communications en temps réel",
        "subtitle": "Fonctionne entièrement dans votre navigateur. Aucune donnée transmise ou stockée.",
        "start": "Lancer l’analyse avancée",
        "score": "Score de visibilité",
        "risk": "Indicateurs de risque de surveillance",
        "logs": "Journaux d’analyse",
        "ethical": "Passif • côté client • sous contrôle utilisateur • éthique",
        "explain_title": "Qu’est‑ce que cela signifie ?",
        "explain_body": (
            "Cette analyse ne prouve pas une écoute. Elle identifie des conditions techniques "
            "compatibles avec des environnements sensibles ou monitorés (permissions audio, "
            "exposition WebRTC, temporisations anormales). Ce sont des indicateurs, pas une preuve."
        )
    },
    "DE": {
        "title": "Echtzeit‑Analyse der Kommunikationssichtbarkeit",
        "subtitle": "Läuft vollständig im Browser. Keine Datenübertragung oder Speicherung.",
        "start": "Tiefenscan starten",
        "score": "Sichtbarkeits‑Score",
        "risk": "Indikatoren für Überwachungsrisiken",
        "logs": "Scan‑Protokolle",
        "ethical": "Passiv • Client‑seitig • Nutzerkontrolliert • Ethisch",
        "explain_title": "Was bedeutet das?",
        "explain_body": (
            "Diese Analyse beweist keine Überwachung. Sie identifiziert technische Bedingungen, "
            "die mit sensiblen oder überwachten Umgebungen vereinbar sind (Audioberechtigungen, "
            "WebRTC‑Exposition, ungewöhnliches Timing). Es sind Indikatoren, keine Bestätigung."
        )
    }
}

lang = st.selectbox("Language", ["EN", "FR", "DE"], index=0)
T = LANG[lang]

# ======================
# STYLE
# ======================
st.markdown("""
<style>
body { background:#0b0f17; color:#e6edf3; }
.card {
  background:#0f1629;
  border:1px solid #1f2a44;
  border-radius:18px;
  padding:1.6rem;
  margin-bottom:1.2rem;
}
.badge {
  padding:.35rem .9rem;
  border-radius:999px;
  font-size:.75rem;
  font-weight:700;
  display:inline-block;
}
.low { background:#064e3b; color:#6ee7b7; }
.mod { background:#78350f; color:#fde68a; }
.high{ background:#7f1d1d; color:#fecaca; }
.idle{ background:#1f2937; color:#9ca3af; }
.score { font-size:3.4rem; font-weight:900; margin-top:.4rem; }
.muted { color:#9aa4b2; font-size:.85rem; }
pre {
  background:#020617;
  padding:1rem;
  border-radius:12px;
  max-height:260px;
  overflow:auto;
}
.log {
  border-left:3px solid #2563eb;
  padding-left:.8rem;
  margin-bottom:.6rem;
}
button {
  padding:.6rem 1.3rem;
  border-radius:14px;
  border:none;
  background:#2563eb;
  color:white;
  font-weight:600;
}
hr { border-color:#1f2a44; }
</style>
""", unsafe_allow_html=True)

# ======================
# HEADER
# ======================
st.markdown("## 🛡️ CallBreach")
st.caption(T["title"])
st.markdown(f"<div class='muted'>{T['subtitle']}</div>", unsafe_allow_html=True)

# ======================
# ENGINE (CLIENT‑SIDE)
# ======================
components.html(
f"""
<!DOCTYPE html>
<html>
<body style="background:#0f1629;color:#e6edf3;font-family:system-ui">

<div class="card" id="main">
  <span class="badge idle" id="verdictBadge">READY</span>
  <div class="score" id="scoreValue">— / 100</div>
  <div class="muted">{T["score"]}</div>
  <button onclick="runScan()">{T["start"]}</button>
</div>

<div class="card" id="details" style="display:none">
  <strong>Exposure analysis</strong>
  <p id="verdictText"></p>
  <pre id="jsonOut"></pre>
</div>

<div class="card" id="monitor" style="display:none">
  <strong>{T["risk"]}</strong>
  <p id="riskText"></p>
  <pre id="riskJson"></pre>
</div>

<div class="card" id="logs">
  <strong>{T["logs"]}</strong>
  <div id="logList" class="muted">No scan yet.</div>
</div>

<div class="card">
  <strong>{T["explain_title"]}</strong>
  <p class="muted">{T["explain_body"]}</p>
</div>

<script>
let scanCount = 0;

function log(msg) {{
  const el = document.createElement("div");
  el.className = "log";
  el.textContent = new Date().toLocaleTimeString() + " — " + msg;
  const list = document.getElementById("logList");
  if (scanCount === 1) list.innerHTML = "";
  list.prepend(el);
}}

async function runScan() {{
  scanCount++;
  log("Scan initiated");

  const badge = document.getElementById("verdictBadge");
  badge.textContent = "SCANNING…";
  badge.className = "badge mod";
  document.getElementById("scoreValue").textContent = "— / 100";

  const R = {{
    network:{{}},
    device:{{}},
    timing:{{}},
    monitoring:{{}}
  }};

  // =======================
  // NETWORK / WEBRTC
  // =======================
  R.network = {{
    hasTURN:false,
    hasSRFLX:false,
    hasHOST:false,
    mdns:false,
    ipv6:false,
    interfaces:[],
    iceCount:0
  }};

  const pc = new RTCPeerConnection({{
    iceServers:[{{urls:"stun:stun.l.google.com:19302"}}]
  }});
  pc.createDataChannel("cb");

  pc.onicecandidate = e => {{
    if (!e || !e.candidate) return;
    const c = e.candidate.candidate;
    R.network.iceCount++;
    if (c.includes(" typ relay ")) R.network.hasTURN = true;
    if (c.includes(" typ srflx ")) R.network.hasSRFLX = true;
    if (c.includes(" typ host ")) R.network.hasHOST = true;
    if (c.includes(".local")) R.network.mdns = true;
    if (c.toLowerCase().includes("ip6")) R.network.ipv6 = true;

    const ip = c.match(/([0-9]{{1,3}}(\\.[0-9]{{1,3}}){{3}})/);
    if (ip) {{
      const v = ip[1];
      if (v.startsWith("10.") || v.startsWith("192.168.") || v.startsWith("172.")) {{
        if (!R.network.interfaces.includes("LAN")) R.network.interfaces.push("LAN");
      }} else {{
        if (!R.network.interfaces.includes("PUBLIC")) R.network.interfaces.push("PUBLIC");
      }}
    }}
  }};

  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);
  await new Promise(r=>setTimeout(r,2500));
  pc.close();
  log("WebRTC surface analyzed");

  // =======================
  // DEVICE CONTEXT
  // =======================
  R.device = {{
    cores:navigator.hardwareConcurrency || null,
    memory:navigator.deviceMemory || null,
    pixelRatio:window.devicePixelRatio,
    timezone:new Date().getTimezoneOffset(),
    touch:navigator.maxTouchPoints || 0
  }};
  log("Device context collected");

  // =======================
  // TIMING / DRIFT
  // =======================
  let drift=[];
  let t=performance.now();
  for(let i=0;i<6;i++) {{
    await new Promise(r=>setTimeout(r,40));
    drift.push(Math.abs(performance.now()-t-40));
    t=performance.now();
  }}
  R.timing.timerDrift = drift;
  log("Timing drift measured");

  // =======================
  // MONITORING INDICATORS (ETHICAL)
  // =======================
  R.monitoring = {{
    audioDevices:[],
    micPermission:null,
    anomalies:[]
  }};

  if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {{
    const devices = await navigator.mediaDevices.enumerateDevices();
    R.monitoring.audioDevices = devices
      .filter(d => d.kind === "audioinput")
      .map(d => ({{ label: d.label || "hidden" }}));

    if (R.monitoring.audioDevices.length > 1) {{
      R.monitoring.anomalies.push("Multiple audio input devices detected");
    }}
  }}

  if (navigator.permissions) {{
    try {{
      const perm = await navigator.permissions.query({{ name: "microphone" }});
      R.monitoring.micPermission = perm.state;
      if (perm.state === "granted") {{
        R.monitoring.anomalies.push("Microphone permission already granted");
      }}
    }} catch {{}}
  }}

  const avgDrift = drift.reduce((a,b)=>a+b,0)/drift.length;
  if (avgDrift > 8) {{
    R.monitoring.anomalies.push("Abnormal timer drift detected");
  }}

  log("Monitoring indicators evaluated");

  // =======================
  // SCORING
  // =======================
  let score = 100;
  if (R.network.hasHOST) score -= 15;
  if (R.network.hasSRFLX) score -= 20;
  if (!R.network.hasTURN) score -= 15;
  if (R.network.interfaces.includes("PUBLIC")) score -= 20;
  if (R.network.ipv6) score -= 10;
  if (R.network.iceCount > 6) score -= 5;
  score = Math.max(score, 0);

  let cls = "low";
  let verdict = "Low visibility — limited exposure";
  if (score < 75) {{ cls="mod"; verdict="Moderate visibility — partial exposure"; }}
  if (score < 45) {{ cls="high"; verdict="High visibility — strong exposure"; }}

  let monitorScore = 0;
  monitorScore += R.monitoring.audioDevices.length > 1 ? 20 : 0;
  monitorScore += R.monitoring.micPermission === "granted" ? 20 : 0;
  monitorScore += R.monitoring.anomalies.length * 15;
  monitorScore = Math.min(monitorScore, 100);
  R.monitoring.score = monitorScore;

  log("Scoring completed");

  // =======================
  // RENDER
  // =======================
  badge.textContent = verdict;
  badge.className = "badge " + cls;
  document.getElementById("scoreValue").textContent = score + "/100";

  document.getElementById("details").style.display = "block";
  document.getElementById("verdictText").textContent = verdict;
  document.getElementById("jsonOut").textContent = JSON.stringify(R.network, null, 2);

  document.getElementById("monitor").style.display = "block";
  document.getElementById("riskText").textContent =
    "Risk index: " + monitorScore + "/100 — " +
    (monitorScore < 30 ? "No significant indicators" :
     monitorScore < 60 ? "Sensitive environment indicators" :
     "Multiple indicators detected");

  document.getElementById("riskJson").textContent =
    JSON.stringify(R.monitoring, null, 2);

  log("Scan completed");
}}
</script>

</body>
</html>
""",
height=1200
)

st.divider()
st.caption(T["ethical"])
