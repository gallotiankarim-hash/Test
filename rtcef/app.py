import streamlit as st
import yaml
from pathlib import Path
import streamlit.components.v1 as components

# ==================================================
# LOAD POLICY
# ==================================================
policy = yaml.safe_load(Path("policy.yaml").read_text())
APP_NAME = policy["app"]["name"]

# ==================================================
# LANGUAGE SELECTOR
# ==================================================
LANGS = {
    "EN": {
        "title": "Real‑time communication visibility assessment",
        "intro": "This assessment runs entirely in your browser. No data is transmitted, stored or shared.",
        "start": "Start visibility scan",
        "ready": "READY",
        "scanning": "SCANNING…",
        "score": "Visibility score",
        "explain_title": "What does this mean?",
        "low": "Your exposure during calls is low. Your network hides most technical signals.",
        "mod": "Some technical signals are visible. Your exposure is moderate.",
        "high": "Your device exposes several network signals. Your visibility during calls is high.",
        "footer": "Passive, client‑side, ethical by design — no identification, no tracking."
    },
    "FR": {
        "title": "Évaluation de visibilité des communications temps réel",
        "intro": "Cette analyse s’exécute entièrement dans votre navigateur. Aucune donnée n’est transmise, stockée ou partagée.",
        "start": "Démarrer l’analyse",
        "ready": "PRÊT",
        "scanning": "ANALYSE…",
        "score": "Score de visibilité",
        "explain_title": "Qu’est‑ce que cela signifie ?",
        "low": "Votre exposition lors des appels est faible. Votre réseau masque la majorité des signaux techniques.",
        "mod": "Certains signaux techniques sont visibles. Votre exposition est modérée.",
        "high": "Votre appareil expose plusieurs signaux réseau. Votre visibilité lors des appels est élevée.",
        "footer": "Passif, côté client, éthique par conception — aucune identification, aucun traçage."
    },
    "DE": {
        "title": "Sichtbarkeitsbewertung von Echtzeitkommunikation",
        "intro": "Diese Analyse läuft vollständig in Ihrem Browser. Es werden keine Daten übertragen, gespeichert oder geteilt.",
        "start": "Scan starten",
        "ready": "BEREIT",
        "scanning": "ANALYSE…",
        "score": "Sichtbarkeitswert",
        "explain_title": "Was bedeutet das?",
        "low": "Ihre Sichtbarkeit während Anrufen ist gering.",
        "mod": "Einige technische Signale sind sichtbar. Mittlere Sichtbarkeit.",
        "high": "Ihr Gerät gibt mehrere Netzwerksignale preis. Hohe Sichtbarkeit.",
        "footer": "Passiv, clientseitig, ethisch konzipiert — keine Identifikation, kein Tracking."
    }
}

lang = st.selectbox("Language", list(LANGS.keys()), index=0)
T = LANGS[lang]

# ==================================================
# PAGE CONFIG & STYLE
# ==================================================
st.set_page_config(page_title=APP_NAME, page_icon="🛡️", layout="centered")

st.markdown("""
<style>
body { background:#0b0f17; color:#e6edf3; }
.card {
  background:#0f1629;
  border:1px solid #1f2a44;
  border-radius:18px;
  padding:1.8rem;
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
button { cursor:pointer; }
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================
st.markdown(f"## 🛡️ {APP_NAME}")
st.caption(T["title"])
st.divider()
st.markdown(f"<div class='muted'>{T['intro']}</div>", unsafe_allow_html=True)

# ==================================================
# CLIENT-SIDE WEBRTC SCAN
# ==================================================
components.html(
f"""
<!DOCTYPE html>
<html>
<body style="background:#0f1629;color:#e6edf3;font-family:system-ui">

<div id="card" class="card">
  <span class="badge idle">{T["ready"]}</span>
  <div class="score">— / 100</div>
  <div class="muted">{T["score"]}</div>

  <button onclick="runScan()" style="
    margin-top:1rem;
    padding:.6rem 1.2rem;
    border-radius:12px;
    border:none;
    background:#2563eb;
    color:white;
    font-weight:600;">
    ▶ {T["start"]}
  </button>
</div>

<div id="explain" class="card" style="display:none"></div>

<script>
async function runScan() {{
  document.getElementById("card").innerHTML = `
    <span class="badge mod">{T["scanning"]}</span>
    <div class="score">— / 100</div>
    <div class="muted">{T["score"]}</div>
  `;

  const r = {{
    hasTURN:false, hasSRFLX:false, hasHOST:false,
    ipv6:false, mdns:false, interfaces:[]
  }};

  const pc = new RTCPeerConnection({{iceServers:[{{urls:"stun:stun.l.google.com:19302"}}]}});
  pc.createDataChannel("cb");

  pc.onicecandidate = e => {{
    if (!e || !e.candidate) return;
    const c = e.candidate.candidate;
    if (c.includes(" typ relay ")) r.hasTURN = true;
    if (c.includes(" typ srflx ")) r.hasSRFLX = true;
    if (c.includes(" typ host ")) r.hasHOST = true;
    if (c.includes(".local")) r.mdns = true;
    if (c.toLowerCase().includes("ip6")) r.ipv6 = true;

    const ip = c.match(/([0-9]{{1,3}}(\\.[0-9]{{1,3}}){{3}})/);
    if (ip) {{
      const v = ip[1];
      if (v.startsWith("10.") || v.startsWith("192.168.") || v.startsWith("172.")) {{
        if (!r.interfaces.includes("LAN")) r.interfaces.push("LAN");
      }} else {{
        if (!r.interfaces.includes("PUBLIC")) r.interfaces.push("PUBLIC");
      }}
    }}
  }};

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

  let verdictText = score < 45 ? "{T['high']}" : score < 75 ? "{T['mod']}" : "{T['low']}";
  let cls = score < 45 ? "high" : score < 75 ? "mod" : "low";

  // UPDATE UI
  const card = document.getElementById("card");
  card.innerHTML = `
    <span class="badge" id="verdict"></span>
    <div class="score">${{score}}/100</div>
    <div class="muted">{T["score"]}</div>
  `;
  const verdictElem = document.getElementById("verdict");
  verdictElem.textContent = verdictText;
  verdictElem.className = "badge " + cls;

  const explain = document.getElementById("explain");
  explain.style.display = "block";
  explain.innerHTML = `
    <strong>{T["explain_title"]}</strong>
    <p style="margin-top:.5rem">${verdictText}</p>
    <pre style="margin-top:1rem">${{JSON.stringify(r,null,2)}}</pre>
  `;
}}
</script>

</body>
</html>
""",
height=720
)

st.divider()
st.caption(T["footer"])
