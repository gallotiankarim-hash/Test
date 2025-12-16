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
        "logs": "Scan logs",
        "ethical": "Passive • client‑side • owner‑controlled • ethical by design"
    },
    "FR": {
        "title": "Évaluation de la visibilité des communications en temps réel",
        "subtitle": "Fonctionne entièrement dans votre navigateur. Aucune donnée transmise ou stockée.",
        "start": "Lancer l’analyse avancée",
        "score": "Score de visibilité",
        "logs": "Journaux d’analyse",
        "ethical": "Passif • côté client • sous contrôle utilisateur • éthique"
    },
    "DE": {
        "title": "Echtzeit‑Analyse der Kommunikationssichtbarkeit",
        "subtitle": "Läuft vollständig im Browser. Keine Datenübertragung oder Speicherung.",
        "start": "Tiefenscan starten",
        "score": "Sichtbarkeits‑Score",
        "logs": "Scan‑Protokolle",
        "ethical": "Passiv • Client‑seitig • Nutzerkontrolliert • Ethisch"
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
  margin-bottom:.8rem;
}
button {
  padding:.6rem 1.3rem;
  border-radius:14px;
  border:none;
  background:#2563eb;
  color:white;
  font-weight:600;
}
</style>
""", unsafe_allow_html=True)

# ======================
# HEADER
# ======================
st.markdown("## 🛡️ CallBreach")
st.caption(T["title"])
st.markdown(f"<div class='muted'>{T['subtitle']}</div>", unsafe_allow_html=True)

# ======================
# ENGINE
# ======================
components.html(
f"""
<!DOCTYPE html>
<html>
<body style="background:#0f1629;color:#e6edf3;font-family:system-ui">

<div class="card" id="main">
  <span class="badge idle">READY</span>
  <div class="score">— / 100</div>
  <div class="muted">{T["score"]}</div>
  <button onclick="runScan()">{T["start"]}</button>
</div>

<div class="card" id="details" style="display:none">
  <strong>Exposure analysis</strong>
  <p id="verdictText"></p>
  <pre id="jsonOut"></pre>
</div>

<div class="card" id="logs">
  <strong>{T["logs"]}</strong>
  <div id="logList" class="muted">No scan yet.</div>
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
  document.getElementById("main").innerHTML = `
    <span class="badge mod">SCANNING…</span>
    <div class="score">— / 100</div>
    <div class="muted">Analyzing communication surface…</div>
  `;

  const R = {{
    network:{{}},
    device:{{}},
    timing:{{}}
  }};

  R.network = {{
    hasTURN:false,
    hasSRFLX:false,
    hasHOST:false,
    mdns:false,
    ipv6:false,
    interfaces:[]
  }};

  const pc = new RTCPeerConnection({{
    iceServers:[{{urls:"stun:stun.l.google.com:19302"}}]
  }});

  pc.createDataChannel("cb");

  pc.onicecandidate = e => {{
    if (!e || !e.candidate) return;
    const c = e.candidate.candidate;
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

  R.device = {{
    cores:navigator.hardwareConcurrency || null,
    memory:navigator.deviceMemory || null,
    pixelRatio:window.devicePixelRatio,
    timezone:new Date().getTimezoneOffset()
  }};

  let score = 100;
  if (R.network.hasHOST) score -= 15;
  if (R.network.hasSRFLX) score -= 20;
  if (!R.network.hasTURN) score -= 15;
  if (R.network.interfaces.includes("PUBLIC")) score -= 20;
  if (R.network.ipv6) score -= 10;
  score = Math.max(score, 0);

  let cls = "low";
  let verdict = "Low visibility — limited exposure";
  if (score < 75) {{ cls="mod"; verdict="Moderate visibility — partial exposure"; }}
  if (score < 45) {{ cls="high"; verdict="High visibility — strong exposure"; }}

  log("Scan completed — score " + score);

  document.getElementById("main").innerHTML = `
    <span class="badge ${cls}">${verdict}</span>
    <div class="score">${score}/100</div>
    <div class="muted">{T["score"]}</div>
  `;

  document.getElementById("details").style.display = "block";
  document.getElementById("verdictText").textContent = verdict;
  document.getElementById("jsonOut").textContent = JSON.stringify(R, null, 2);
}}
</script>

</body>
</html>
""",
height=950
)

st.divider()
st.caption(T["ethical"])
