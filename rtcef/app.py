import streamlit as st
from core.session import Session
from core.exposure import ExposureEngine
from core.scoring import score
from capture.mock import generate_mock_flows

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="CallBreach — Real‑Time Exposure Detector",
    page_icon="🚨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==================================================
# LANGUAGE SELECTION
# ==================================================
LANG = st.query_params.get("lang", "en")

# ==================================================
# TRANSLATIONS
# ==================================================
TEXT = {
    "en": {
        "app_title": "CallBreach",
        "tagline": "Real‑time communication exposure detector",
        "safe": "SAFE",
        "exposed": "EXPOSED",
        "critical": "CRITICAL",
        "safe_sub": "No exposure detected",
        "exposed_sub": "Network exposure detected",
        "critical_sub": "High exposure detected",
        "safe_txt": (
            "Your environment does not appear to expose identifiable network information "
            "during real‑time communications.\n\n"
            "This suggests your calls are handled in a privacy‑preserving manner."
        ),
        "exposed_txt": (
            "Your device appears to reveal certain technical network identifiers "
            "when establishing real‑time calls.\n\n"
            "This does not mean your calls are listened to, "
            "but it indicates reduced network privacy."
        ),
        "critical_txt": (
            "A high level of network exposure was detected during real‑time communication.\n\n"
            "This configuration may significantly reduce your privacy."
        ),
        "bubble_safe": "No immediate privacy risk detected.",
        "bubble_exposed": "Some network identifiers may be exposed during calls.",
        "bubble_critical": "High exposure detected. Network privacy may be reduced.",
        "what_title": "What does this mean?",
        "what_txt": (
            "Internet‑based calls sometimes require your device to share technical "
            "network information to function.\n\n"
            "CallBreach evaluates whether this information could reduce your privacy.\n\n"
            "• This tool does not listen to calls\n"
            "• It does not identify other people\n"
            "• It only evaluates your own network exposure"
        ),
        "tech": "Show technical details (advanced)",
        "footer": (
            "CallBreach performs a passive analysis of your environment. "
            "Results are informational and do not imply compromise."
        )
    },

    "fr": {
        "app_title": "CallBreach",
        "tagline": "Détecteur d’exposition des communications en temps réel",
        "safe": "SÉCURISÉ",
        "exposed": "EXPOSÉ",
        "critical": "CRITIQUE",
        "safe_sub": "Aucune exposition détectée",
        "exposed_sub": "Exposition réseau détectée",
        "critical_sub": "Exposition élevée détectée",
        "safe_txt": (
            "Votre environnement ne semble pas exposer d’informations réseau identifiables "
            "lors des communications en temps réel.\n\n"
            "Cela indique un niveau de confidentialité satisfaisant."
        ),
        "exposed_txt": (
            "Votre appareil semble révéler certains identifiants techniques "
            "lors de l’établissement d’appels.\n\n"
            "Cela ne signifie pas que vos appels sont écoutés, "
            "mais que votre confidentialité réseau est réduite."
        ),
        "critical_txt": (
            "Une exposition réseau élevée a été détectée lors des communications.\n\n"
            "Cette configuration peut fortement réduire votre confidentialité."
        ),
        "bubble_safe": "Aucun risque immédiat détecté.",
        "bubble_exposed": "Certains identifiants réseau peuvent être exposés.",
        "bubble_critical": "Exposition élevée détectée. Confidentialité réduite.",
        "what_title": "Que signifie ce résultat ?",
        "what_txt": (
            "Les appels via Internet nécessitent parfois le partage "
            "d’informations techniques réseau.\n\n"
            "CallBreach évalue si ces informations peuvent affecter votre confidentialité.\n\n"
            "• Aucun contenu d’appel n’est analysé\n"
            "• Aucune autre personne n’est identifiée\n"
            "• Seule votre exposition réseau est évaluée"
        ),
        "tech": "Afficher les détails techniques (avancé)",
        "footer": (
            "CallBreach effectue une analyse passive de votre environnement. "
            "Les résultats sont informatifs et n’indiquent pas une compromission."
        )
    },

    "de": {
        "app_title": "CallBreach",
        "tagline": "Echtzeit‑Detektor für Kommunikations‑Exposition",
        "safe": "SICHER",
        "exposed": "EXPOSIERT",
        "critical": "KRITISCH",
        "safe_sub": "Keine Exposition festgestellt",
        "exposed_sub": "Netzwerkexposition erkannt",
        "critical_sub": "Hohe Exposition erkannt",
        "safe_txt": (
            "Ihre Umgebung scheint während Echtzeit‑Kommunikation "
            "keine identifizierbaren Netzwerkdaten preiszugeben.\n\n"
            "Dies deutet auf ein gutes Datenschutzniveau hin."
        ),
        "exposed_txt": (
            "Ihr Gerät gibt beim Aufbau von Echtzeit‑Anrufen "
            "bestimmte technische Netzwerkdaten preis.\n\n"
            "Dies bedeutet nicht, dass Gespräche abgehört werden, "
            "sondern dass der Datenschutz reduziert ist."
        ),
        "critical_txt": (
            "Eine hohe Netzwerkexposition wurde festgestellt.\n\n"
            "Diese Konfiguration kann Ihre Privatsphäre erheblich beeinträchtigen."
        ),
        "bubble_safe": "Kein unmittelbares Datenschutzrisiko erkannt.",
        "bubble_exposed": "Einige Netzwerkkennungen könnten sichtbar sein.",
        "bubble_critical": "Hohe Exposition erkannt. Datenschutz reduziert.",
        "what_title": "Was bedeutet das?",
        "what_txt": (
            "Internetbasierte Anrufe erfordern manchmal die Weitergabe "
            "technischer Netzwerkdaten.\n\n"
            "CallBreach bewertet, ob diese Daten Ihre Privatsphäre beeinträchtigen.\n\n"
            "• Keine Gesprächsinhalte werden analysiert\n"
            "• Keine anderen Personen werden identifiziert\n"
            "• Nur Ihre eigene Netzwerkexposition wird bewertet"
        ),
        "tech": "Technische Details anzeigen (erweitert)",
        "footer": (
            "CallBreach führt eine passive Analyse Ihrer Umgebung durch. "
            "Die Ergebnisse dienen nur zur Information."
        )
    }
}

T = TEXT.get(LANG, TEXT["en"])

# ==================================================
# STYLE (CSS)
# ==================================================
st.markdown("""
<style>
body { background-color: #0e1117; }
.status-box {
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    margin-bottom: 2rem;
}
.safe { background: linear-gradient(135deg,#0f5132,#198754); color:white; }
.exposed { background: linear-gradient(135deg,#664d03,#ffc107); color:#0e1117; }
.critical { background: linear-gradient(135deg,#58151c,#dc3545); color:white; }
.badge {
    padding:0.4rem 0.9rem;
    border-radius:999px;
    font-weight:600;
    font-size:0.85rem;
    display:inline-block;
}
.small { color:#8b949e; font-size:0.85rem; }
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================
st.markdown(f"## 🔍 {T['app_title']}")
st.markdown(f"<span class='small'>{T['tagline']}</span>", unsafe_allow_html=True)
st.divider()

# ==================================================
# AUTO ANALYSIS
# ==================================================
session = Session()
engine = ExposureEngine()

for flow in generate_mock_flows():
    session.add_flow(flow)
    for f in engine.analyze(flow):
        session.add_finding(f)

exposure_score = score(session.findings)

if exposure_score == 0:
    status = "SAFE"
elif exposure_score < 40:
    status = "EXPOSED"
else:
    status = "CRITICAL"

# ==================================================
# STATUS MAP
# ==================================================
MAP = {
    "SAFE": ("safe", T["safe"], T["safe_sub"], T["safe_txt"]),
    "EXPOSED": ("exposed", T["exposed"], T["exposed_sub"], T["exposed_txt"]),
    "CRITICAL": ("critical", T["critical"], T["critical_sub"], T["critical_txt"])
}

css, title, sub, text = MAP[status]

st.markdown(
    f"""
    <div class="status-box {css}">
        <div class="badge">{title}</div>
        <h2>{sub}</h2>
        <p>{text}</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ==================================================
# NOTIFICATIONS
# ==================================================
if status == "SAFE":
    st.success(T["bubble_safe"])
elif status == "EXPOSED":
    st.warning(T["bubble_exposed"])
else:
    st.error(T["bubble_critical"])

# ==================================================
# EXPLANATION
# ==================================================
st.markdown(f"### 🧠 {T['what_title']}")
st.markdown(T["what_txt"])

# ==================================================
# TECH DETAILS
# ==================================================
with st.expander(f"🔧 {T['tech']}"):
    st.json({
        "status": status,
        "score": exposure_score,
        "findings": session.findings
    })

# ==================================================
# FOOTER
# ==================================================
st.divider()
st.markdown(f"<div class='small'>{T['footer']}</div>", unsafe_allow_html=True)
