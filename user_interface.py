# user_interface.py
# PPUM Smart Triage Kiosk (blue theme, background photo, EN/BM toggle,
# large-text mode, live clock and printable queue ticket)
#
# Keep these next to this file:
#   background.jpg          (lobby photo)
#   .streamlit/config.toml  (blue theme colours for toggles and buttons)
#   logo.png                (optional, replaces the cross icon in the header)

import base64
import datetime
import html
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

try:
    from zoneinfo import ZoneInfo
    MY_TZ = ZoneInfo("Asia/Kuala_Lumpur")
except Exception:  # tzdata missing (some Windows installs)
    MY_TZ = None

BASE_DIR = Path(__file__).parent

# AI symptom extraction (needs llm_extraction.py, system_prompt.py, triage_rules.py, openai, OPENAI_API_KEY)
try:
    from llm_extraction import classify as ai_classify
    AI_READY = True
except Exception:
    AI_READY = False


def now_my() -> datetime.datetime:
    return datetime.datetime.now(MY_TZ) if MY_TZ else datetime.datetime.now()


def panel(name: str):
    """Bordered panel. The key lets the stylesheet style only these panels (needs Streamlit 1.39+)."""
    try:
        return st.container(border=True, key=f"panel_{name}")
    except TypeError:
        return st.container(border=True)


def build_patient_payload(age, gender_code: str, history: str, symptoms_lower: str) -> str:
    """
    Combine the separate form fields into one string with the exact layout the LLM
    examples (ICL) use:   Age / Gender / History / Symptoms
    Gender is always sent in English, whatever language the kiosk is showing.
    """
    gender_en = T["en"][gender_code]                      # "Male" / "Female" / "Other"
    history_clean = " ".join(history.split()) or "None"
    symptoms_clean = " ".join(symptoms_lower.split()).replace('"', "'")
    return "\n".join([
        f"Age: {age}",
        f"Gender: {gender_en}",
        f"History: {history_clean}",
        f'Symptoms: "{symptoms_clean}"',
    ])


def file_to_data_uri(path: Path, mime: str) -> str:
    if not path.exists():
        return ""
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def embed_html(code: str, height: int):
    """Render a small HTML snippet. Uses st.iframe on new Streamlit, components.html on older ones."""
    if hasattr(st, "iframe"):
        st.iframe(code.strip(), height=height)
    else:
        components.html(code, height=height)


st.set_page_config(page_title="PPUM Smart Triage Kiosk", page_icon="🏥", layout="centered")

# ------------------------------------------------------------------
# TEXT (English / Bahasa Malaysia)
# ------------------------------------------------------------------
T = {
    "en": {
        "org": "Emergency Department",
        "hospital": "Pusat Perubatan Universiti Malaya",
        "sub": "Smart Triage Receptionist",
        "tile1": "Your details", "tile2": "Referral", "tile3": "Symptoms",
        "s1": "Patient details", "s2": "Referral status", "s3": "Chief complaint",
        "name": "Name", "name_ph": "Enter full name",
        "age": "Age", "date": "Date", "time": "Time", "gender": "Gender",
        "m": "Male", "f": "Female", "o": "Other",
        "referred": "Referred case?", "yes": "Yes", "no": "No",
        "ref_as": "Referred as", "ref_ph": "e.g., Klinik Kesihatan",
        "symptoms": "Describe your main symptoms",
        "sym_ph": "e.g., I have severe chest pain and I am sweating...",
        "history": "Past medical history (optional)", "hist_ph": "e.g., Asthma, Diabetes",
        "staff": "Clinical vitals · Staff use only",
        "general": "General condition", "conscious": "Conscious?", "gcs": "GCS score",
        "vitals": "Vital signs", "pulse": "Pulse", "resp": "Resp. rate", "bp": "BP",
        "spo2": "SpO2", "temp": "Temp", "pain": "Pain scale", "exam": "Examination findings",
        "submit": "Get my triage result",
        "analysing": "Analysing your symptoms...",
        "detected": "Detected symptoms",
        "warn": "Chief complaint missing. Please describe your symptoms.",
        "status": "Status", "wait": "Wait time",
        "ticket": "Queue ticket", "queue_no": "Queue no.", "zone": "Zone",
        "print": "Print ticket", "new": "Start for a new patient",
        "show_nurse": "Show this ticket to the nurse.",
        "footer": "If you feel very unwell at any time, tell a staff member straight away.",
        "red": {"zone": "RED ZONE", "level": "Critical / Resuscitation",
                "status": "Critical symptoms detected", "wait": "Immediate care",
                "action": "Go IMMEDIATELY to the Resuscitation Bay."},
        "amber": {"zone": "YELLOW ZONE", "level": "Semi-critical / Urgent",
                  "status": "Further assessment needed", "wait": "Within 30 minutes",
                  "action": "Go to the Primary Triage Counter."},
        "green": {"zone": "GREEN ZONE", "level": "Non-critical / Outpatient",
                  "status": "Stable, able to walk", "wait": "60 – 120 minutes",
                  "action": "Go to the Standard Outpatient Clinic waiting area."},
    },
    "ms": {
        "org": "Jabatan Perubatan Kecemasan",
        "hospital": "Pusat Perubatan Universiti Malaya",
        "sub": "Penyambut Tetamu Triaj Pintar",
        "tile1": "Maklumat anda", "tile2": "Rujukan", "tile3": "Simptom",
        "s1": "Maklumat pesakit", "s2": "Status rujukan", "s3": "Aduan utama kesihatan",
        "name": "Nama", "name_ph": "Masukkan nama penuh",
        "age": "Umur", "date": "Tarikh", "time": "Masa", "gender": "Jantina",
        "m": "Lelaki", "f": "Perempuan", "o": "Lain-lain",
        "referred": "Kes rujukan?", "yes": "Ya", "no": "Tidak",
        "ref_as": "Rujukan sebagai", "ref_ph": "cth: Klinik Kesihatan",
        "symptoms": "Nyatakan aduan utama anda",
        "sym_ph": "cth: Saya sakit dada yang teruk dan berpeluh...",
        "history": "Sejarah perubatan (pilihan)", "hist_ph": "cth: Asma, Kencing manis",
        "staff": "Tanda vital klinikal · Untuk kakitangan sahaja",
        "general": "Keadaan am pesakit", "conscious": "Sedar diri?", "gcs": "Skor GCS",
        "vitals": "Tanda vital", "pulse": "Kadar nadi", "resp": "Kadar pernafasan",
        "bp": "Tekanan darah", "spo2": "SpO2", "temp": "Suhu badan",
        "pain": "Skala kesakitan", "exam": "Dapatan pemeriksaan",
        "submit": "Dapatkan keputusan saringan",
        "analysing": "Menganalisis simptom anda...",
        "detected": "Simptom dikesan",
        "warn": "Aduan utama tiada. Sila nyatakan simptom anda.",
        "status": "Status", "wait": "Masa menunggu",
        "ticket": "Tiket giliran", "queue_no": "No. giliran", "zone": "Zon",
        "print": "Cetak tiket", "new": "Mula untuk pesakit baru",
        "show_nurse": "Tunjukkan tiket ini kepada jururawat.",
        "footer": "Jika anda berasa sangat tidak sihat, maklumkan kakitangan dengan segera.",
        "red": {"zone": "ZON MERAH", "level": "Kritikal / Resusitasi",
                "status": "Simptom kritikal dikesan", "wait": "Rawatan segera",
                "action": "Pergi SEGERA ke Bilik Resusitasi."},
        "amber": {"zone": "ZON KUNING", "level": "Separa kritikal / Segera",
                  "status": "Penilaian lanjut diperlukan", "wait": "Dalam 30 minit",
                  "action": "Pergi ke Kaunter Triaj Utama."},
        "green": {"zone": "ZON HIJAU", "level": "Tidak kritikal / Pesakit luar",
                  "status": "Stabil, boleh berjalan", "wait": "60 – 120 minit",
                  "action": "Pergi ke ruang menunggu Klinik Pesakit Luar."},
    },
}

ZONE_COLOR = {"red": "#C62828", "amber": "#E08A00", "green": "#2E7D32"}
ZONE_PREFIX = {"red": "R", "amber": "Y", "green": "G"}

# Keywords that decide the zone (English + Malay)
RED_WORDS = ["chest pain", "sweating", "sakit dada", "berpeluh"]
GREEN_WORDS = ["sore throat", "runny nose", "sakit tekak", "hidung berair"]

# ------------------------------------------------------------------
# STATE
# ------------------------------------------------------------------
if "result" not in st.session_state:
    st.session_state.result = None
if "counters" not in st.session_state:
    st.session_state.counters = {"red": 0, "amber": 0, "green": 0}


def new_patient():
    st.session_state.result = None
    for key in ("name", "symptoms", "history", "referral_source"):
        st.session_state[key] = ""


# ------------------------------------------------------------------
# STYLE
# Palette: sky #EAF3FA · blue #41A8C4 · deep blue #2B869F · navy #14304A
# Triage:  red #C62828 · amber #E08A00 · green #2E7D32
# ------------------------------------------------------------------
bg_uri = file_to_data_uri(BASE_DIR / "background.jpg", "image/jpeg")
bg_css = (
    f"linear-gradient(rgba(234,243,250,.40), rgba(234,243,250,.40)), url('{bg_uri}')"
    if bg_uri else "linear-gradient(160deg, #EAF3FA, #BFD9EE)"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --blue: #41A8C4;
    --blue-dark: #2B869F;
    --blue-glass: rgba(65,168,196,.72);
    --navy: #14304A;
    --muted: #4E6A82;
    --line: #BFE0EA;
    --paper: rgba(255,255,255,.58);
    --s: 1;
}

html, body, .stApp, .stApp p, .stApp label, .stApp input, .stApp textarea, .stApp button,
.stApp li, .stApp h1, .stApp h2, .stApp h3, .stApp div[data-baseweb],
.stApp [data-testid="stMarkdownContainer"] *, .stApp [data-testid="stSelectbox"] *, .stApp [data-testid="stDateInput"] *,
.stApp span:not([class*="material"]):not([data-testid="stIconMaterial"]) {
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
}
.stApp { color: var(--navy); }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDeployButton"], .stDeployButton { display: none !important; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 820px; padding-top: 1.2rem; padding-bottom: 3rem; }
iframe { border: 0 !important; }

/* ---------- Top bar: no box, no background ---------- */
.st-key-panel_controls {
    background: transparent !important; border: none !important; box-shadow: none !important;
    backdrop-filter: none !important; padding: 0 0 12px 0 !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.st-key-panel_controls) { border: none !important; background: transparent !important; box-shadow: none !important; }

/* ---------- Header ---------- */
.kiosk-header {
    background: var(--blue-glass);
    color: #fff;
    text-shadow: 0 1px 3px rgba(20,48,74,.45);
    backdrop-filter: blur(4px);
    border-radius: 8px;
    padding: 30px 28px 28px 28px;
    margin: 6px 0 24px 0;
    text-align: center;
    box-shadow: 0 8px 24px rgba(20,48,74,.18);
}
.kiosk-header .org { color: #fff; font-size: 1.15rem; font-weight: 600; margin: 0; }
.kiosk-header h1 {
    color: #fff !important;
    font-size: 2.4rem; font-weight: 700; font-style: normal; letter-spacing: -0.01em;
    line-height: 1.15; margin: 8px 0 0 0; padding: 0;
}
.kiosk-header .sub { color: #fff; font-size: 1.25rem; font-weight: 600; margin: 10px 0 0 0; }
.kiosk-logo { height: 54px; margin-bottom: 8px; }

/* ---------- Section bars ---------- */
.step-bar {
    background: var(--blue-glass);
    color: #fff;
    text-shadow: 0 1px 3px rgba(20,48,74,.45);
    border-radius: 8px;
    padding: 14px 22px;
    margin: 26px 0 10px 0;
    font-size: 1.5rem;
    font-weight: 700;
    box-shadow: 0 3px 10px rgba(20,48,74,.12);
}

/* ---------- Panels ---------- */
[class*="st-key-panel_"] {
    background: var(--paper);
    border: 1px solid rgba(255,255,255,.7);
    border-radius: 8px;
    padding: 12px 14px;
    box-shadow: 0 4px 16px rgba(20,48,74,.10);
    backdrop-filter: blur(6px);
}
div[data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-panel_"]):not(:has(div[data-testid="stVerticalBlockBorderWrapper"] [class*="st-key-panel_"])) { border-color: transparent !important; }

/* ---------- Labels and inputs (larger) ---------- */
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span, [data-testid="stWidgetLabel"] label, .stApp label {
    font-size: 1.3rem !important;
    font-weight: 600 !important;
    color: var(--navy) !important;
}
.sub-label { font-size: 1.3rem; font-weight: 700; color: var(--navy); margin: 14px 0 6px 0; }

.stTextInput input, .stNumberInput input, .stDateInput input,
.stTextArea textarea, div[data-baseweb="select"] > div, div[data-baseweb="select"] div[value] {
    font-size: 1.3rem !important;
    border-radius: 6px !important;
    border: 1.5px solid var(--line) !important;
    background: rgba(255,255,255,.80) !important;
    color: var(--navy) !important;
}
.stTextInput input, .stNumberInput input, .stDateInput input, div[data-baseweb="select"] > div { min-height: 62px; }
[data-testid="stTextInputRootElement"], [data-testid="stNumberInputContainer"] { min-height: 62px !important; height: auto !important; }
[data-testid="stTextInputRootElement"] input, [data-testid="stNumberInputContainer"] input { height: 62px; }
/* dropdown and date field text (works across Streamlit versions) */
[data-testid="stSelectbox"] div, [data-testid="stSelectbox"] input, [data-testid="stSelectbox"] span,
[data-testid="stDateInputField"], [data-testid="stDateInputField"] *, [data-testid="stDateInput"] input {
    font-size: 1.3rem !important; color: var(--navy) !important;
}
[data-testid="stSelectbox"] [role="group"], [data-testid="stDateInputField"] {
    min-height: 62px; border: 1.5px solid var(--line); border-radius: 6px; background: rgba(255,255,255,.80);
}
[data-testid="stSelectbox"] [role="group"] { height: 62px; }
[data-testid="stSelectbox"] input[role="combobox"], [data-testid="stSelectbox"] button { min-height: 62px; height: 62px; }
[data-testid="stSelectbox"] [data-baseweb="select"] > div, [data-testid="stDateInputField"] { min-height: 62px; align-items: center; }
.stTextArea textarea { min-height: 150px; }
.stTextInput input::placeholder, .stTextArea textarea::placeholder { font-size: 1.2rem; color: #7C93A5; }
ul[role="listbox"] li, ul[role="listbox"] li * { font-size: 1.2rem !important; }
.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(65,168,196,.30) !important;
}

/* ---------- Radio buttons shown as option buttons ---------- */
div[role="radiogroup"] { gap: 10px; }
div[role="radiogroup"] label {
    background: transparent; border: 1.5px solid rgba(20,48,74,.45);
    border-radius: 6px; padding: 12px 22px; margin: 0;
}
div[role="radiogroup"] label p, label[data-baseweb="radio"] p, label[data-testid="stRadioOption"] p {
    font-size: 1.25rem !important; font-weight: 600 !important; color: var(--navy) !important;
}
/* selected option: every known way Streamlit marks it */
div[role="radiogroup"] label[data-selected="true"],
div[role="radiogroup"] label[aria-checked="true"],
div[role="radiogroup"] label:has(input:checked),
div[role="radiogroup"] label:has(input[aria-checked="true"]),
div[role="radiogroup"] label:has([aria-checked="true"]),
div[role="radiogroup"] label:has(input[checked]:not([tabindex="-1"])) {
    background: var(--blue) !important; border-color: var(--blue-dark) !important;
}
div[role="radiogroup"] label[data-selected="true"] p,
div[role="radiogroup"] label[aria-checked="true"] p,
div[role="radiogroup"] label:has(input:checked) p,
div[role="radiogroup"] label:has(input[aria-checked="true"]) p,
div[role="radiogroup"] label:has([aria-checked="true"]) p { color: #fff !important; }

/* ---------- Staff expander ---------- */
div[data-testid="stExpander"] {
    background: var(--paper);
    border: 1.5px dashed #8FCADA !important;
    border-radius: 8px !important;
    margin-top: 26px;
}
div[data-testid="stExpander"] summary p, div[data-testid="stExpander"] summary span {
    font-size: 1.3rem !important; font-weight: 700 !important; color: var(--blue-dark) !important;
}

/* ---------- Buttons ---------- */
.stButton > button, .stButton > button[kind="primary"], .stButton > button[kind="secondary"] {
    background: var(--blue) !important; color: #fff !important;
    border: none !important; border-radius: 8px; min-height: 74px;
    box-shadow: 0 5px 14px rgba(43,134,159,.35);
    transition: background .15s ease;
}
.stButton > button p, .stButton > button div, .stButton > button span {
    color: #fff !important; font-size: 1.45rem !important; font-weight: 700 !important;
}
.stButton > button:hover { background: var(--blue-dark) !important; }
.stButton > button:focus-visible { outline: 4px solid #A6DCEA; outline-offset: 2px; }

/* ---------- Triage result ---------- */
.triage-card {
    background: #fff; border-radius: 8px; overflow: hidden;
    margin: 26px 0 14px 0;
    box-shadow: 0 10px 28px rgba(20,48,74,.20);
}
.triage-top { padding: 28px 30px 22px 30px; color: #fff; }
.triage-top .zone { color: #fff !important; font-size: 2.7rem; font-weight: 800; line-height: 1.1; margin: 0; }
.triage-top .level { color: #fff; font-size: 1.3rem; font-weight: 600; margin: 8px 0 0 0; opacity: .95; }
.triage-body { padding: 22px 30px 28px 30px; }
.triage-facts { display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 20px; }
.triage-fact { flex: 1 1 220px; background: #EAF3FA; border-radius: 6px; padding: 14px 18px; }
.triage-fact .k { font-size: 1.05rem; color: var(--muted); font-weight: 600; }
.triage-fact .v { font-size: 1.4rem; font-weight: 800; color: var(--navy); margin-top: 2px; }
.triage-action { font-size: 1.65rem; font-weight: 800; line-height: 1.35; padding-left: 18px; border-left: 8px solid; color: var(--navy); }
.red { animation: pulse 1.6s ease-in-out 3; }
@keyframes pulse { 0%,100% { box-shadow: 0 10px 28px rgba(20,48,74,.20);} 50% { box-shadow: 0 0 0 10px rgba(198,40,40,.28);} }
@media (prefers-reduced-motion: reduce) { .red { animation: none; } }

/* ---------- Footer note (no background) ---------- */
.footer-note {
    color: var(--navy); text-align: center;
    border-top: 2px solid rgba(20,48,74,.22);
    padding: 20px 12px 0 12px; margin-top: 34px;
    font-size: 1.55rem; font-weight: 700; line-height: 1.4;
    text-shadow: 0 0 8px rgba(255,255,255,.95);
    text-wrap: balance;
}

@media (max-width: 600px) {
    .kiosk-header h1 { font-size: 1.8rem; }
    .triage-top .zone { font-size: 2rem; }
    .triage-action { font-size: 1.3rem; }
    .footer-note { font-size: 1.3rem; }
}
</style>
""", unsafe_allow_html=True)

st.markdown(f"<style>.stApp {{ background: {bg_css}; background-size: cover; background-position: center; background-attachment: fixed; }}</style>",
            unsafe_allow_html=True)

# ------------------------------------------------------------------
# TOP CONTROLS: language, large text, live clock
# ------------------------------------------------------------------
with panel("controls"):
    c_lang, c_clock = st.columns([1.6, 1], vertical_alignment="center")
    with c_lang:
        lang_choice = st.radio(
            "Language / Bahasa", ["English", "Bahasa Malaysia"],
            horizontal=True, key="lang", label_visibility="collapsed",
        )
    L = "ms" if lang_choice == "Bahasa Malaysia" else "en"
    t = T[L]
    with c_clock:
        locale = "ms-MY" if L == "ms" else "en-MY"
        embed_html(f"""
        <div id="clk" style="font-family:'Segoe UI',Arial,sans-serif;font-weight:700;color:#14304A;
             text-align:right;font-size:17px;line-height:1.3;text-shadow:0 0 8px rgba(255,255,255,.95)"></div>
        <script>
        function tick() {{
            const d = new Date();
            const date = d.toLocaleDateString('{locale}', {{weekday:'short', day:'numeric', month:'short', year:'numeric'}});
            const time = d.toLocaleTimeString('{locale}', {{hour:'2-digit', minute:'2-digit'}});
            document.getElementById('clk').innerHTML = date + '<br><span style="font-size:26px">' + time + '</span>';
        }}
        tick(); setInterval(tick, 1000);
        </script>""", height=58)

# ------------------------------------------------------------------
# HEADER
# ------------------------------------------------------------------
logo_uri = file_to_data_uri(BASE_DIR / "logo.png", "image/png")
logo_html = f'<img class="kiosk-logo" src="{logo_uri}" alt="PPUM">' if logo_uri else ""


st.markdown(
    f'<div class="kiosk-header">{logo_html}'
    f'<p class="org">{t["org"]}</p>'
    f'<h1>{t["hospital"]}</h1>'
    f'<p class="sub">PPUM · {t["sub"]}</p>'
    f'</div>',
    unsafe_allow_html=True,
)


def step_bar(number: int, text: str):
    st.markdown(f'<div class="step-bar">{number}. {text}</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------
# SECTION 1: PATIENT DETAILS
# ------------------------------------------------------------------
step_bar(1, t["s1"])
with panel("details"):
    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input(t["name"], placeholder=t["name_ph"], key="name")
        age = st.number_input(t["age"], min_value=1, max_value=120, value=25, key="age")
    with col2:
        gender = st.selectbox(t["gender"], ["m", "f", "o"], format_func=lambda k: t[k], key="gender")
        date_visit = st.date_input(t["date"], now_my().date(), key="date_visit")

# ------------------------------------------------------------------
# SECTION 2: REFERRAL
# ------------------------------------------------------------------
step_bar(2, t["s2"])
with panel("referral"):
    col_ref1, col_ref2 = st.columns(2)
    with col_ref1:
        is_referred = st.radio(t["referred"], ["no", "yes"], format_func=lambda k: t[k],
                               horizontal=True, key="is_referred")
    with col_ref2:
        if is_referred == "yes":
            referral_source = st.text_input(t["ref_as"], placeholder=t["ref_ph"], key="referral_source")

# ------------------------------------------------------------------
# SECTION 3: CHIEF COMPLAINT
# ------------------------------------------------------------------
step_bar(3, t["s3"])
with panel("complaint"):
    symptoms = st.text_area(t["symptoms"], placeholder=t["sym_ph"], height=130, key="symptoms")
    history = st.text_input(t["history"], placeholder=t["hist_ph"], key="history")

# ------------------------------------------------------------------
# STAFF-ONLY VITALS
# ------------------------------------------------------------------
with st.expander(t["staff"]):
    st.markdown(f'<div class="sub-label">{t["general"]}</div>', unsafe_allow_html=True)
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        conscious = st.radio(t["conscious"], ["yes", "no"], format_func=lambda k: t[k],
                             horizontal=True, key="conscious")
    with col_g2:
        gcs_score = st.text_input(t["gcs"], placeholder="e.g., 15", key="gcs")

    st.markdown(f'<div class="sub-label">{t["vitals"]}</div>', unsafe_allow_html=True)
    v1, v2, v3 = st.columns(3)
    with v1:
        pulse = st.text_input(t["pulse"], placeholder="bpm", key="pulse")
        resp_rate = st.text_input(t["resp"], placeholder="breaths/min", key="resp_rate")
    with v2:
        bp = st.text_input(t["bp"], placeholder="mmHg", key="bp")
        spo2 = st.text_input(t["spo2"], placeholder="%", key="spo2")
    with v3:
        temp = st.text_input(t["temp"], placeholder="°C", key="temp")
        pain_scale = st.selectbox(t["pain"], [str(i) for i in range(11)], key="pain")

    exam_findings = st.text_area(t["exam"], key="exam")

# ------------------------------------------------------------------
# SUBMIT + TRIAGE LOGIC (same rules as before, now also reads Malay)
# ------------------------------------------------------------------
st.write("")
if st.button(t["submit"], type="primary", use_container_width=True):
    raw_text = symptoms.strip()
    user_input = raw_text.lower()

    if not raw_text:
        st.session_state.result = None
        st.warning(t["warn"])
    else:
        # Safety-net keyword rules (also the fallback when the AI step is unavailable or fails)
        if any(w in user_input for w in RED_WORDS):
            keyword_zone = "red"
        elif any(w in user_input for w in GREEN_WORDS):
            keyword_zone = "green"
        else:
            keyword_zone = "amber"

        zone, extracted = None, []
        if AI_READY:
            # Combine the separate form fields into one structured string for the LLM
            combined_patient_data = build_patient_payload(age, gender, history, user_input)
            with st.spinner(t["analysing"]):
                # Step 1: LLM extracts symptoms. Step 2: rule-based engine (evaluate_triage_level) routes the zone.
                zone, extracted = ai_classify(combined_patient_data)   # the patient's name is never sent
        if zone is None:
            zone = keyword_zone
        if keyword_zone == "red" or conscious == "no":
            zone = "red"          # never let the AI step downgrade an obvious emergency

        st.session_state.counters[zone] += 1
        st.session_state.result = {
            "zone": zone,
            "ticket": f"{ZONE_PREFIX[zone]}-{st.session_state.counters[zone]:03d}",
            "name": patient_name.strip(),
            "age": age,
            "gender": gender,
            "symptoms": extracted,
            "stamp": now_my().strftime("%d/%m/%Y  %I:%M %p"),
        }

# ------------------------------------------------------------------
# RESULT (kept in session so language / text size can change afterwards)
# ------------------------------------------------------------------
res = st.session_state.result
if res:
    z = res["zone"]
    zt = t[z]
    color = ZONE_COLOR[z]

    detected = ", ".join(
        str(x.get("name", x)) if isinstance(x, dict) else str(x) for x in res.get("symptoms", [])
    )
    detected_html = (
        f'<div class="triage-fact" style="flex-basis:100%"><div class="k">{t["detected"]}</div>'
        f'<div class="v">{html.escape(detected)}</div></div>' if detected else ""
    )

    st.markdown(
        f'<div class="triage-card {"red" if z == "red" else ""}">'
        f'<div class="triage-top" style="background:{color}">'
        f'<p class="zone">{zt["zone"]}</p><p class="level">{zt["level"]}</p></div>'
        f'<div class="triage-body"><div class="triage-facts">'
        f'<div class="triage-fact"><div class="k">{t["status"]}</div><div class="v">{zt["status"]}</div></div>'
        f'<div class="triage-fact"><div class="k">{t["wait"]}</div><div class="v">{zt["wait"]}</div></div>'
        f'{detected_html}</div><div class="triage-action" style="border-color:{color}">{zt["action"]}</div></div></div>',
        unsafe_allow_html=True,
    )

    # Printable queue ticket
    who = html.escape(res["name"]) if res["name"] else "-"
    info = f'{res["age"]} · {t[res["gender"]]}'
    embed_html(f"""
    <style>
      body {{ margin:0; font-family:'Segoe UI',Arial,sans-serif; color:#14304A; }}
      .ticket {{ background:#fff; border:2px dashed #8FCADA; border-radius:12px; padding:18px 22px; }}
      .top {{ display:flex; justify-content:space-between; align-items:center; font-weight:700; font-size:14px; color:#2B869F; }}
      .num {{ font-size:54px; font-weight:800; letter-spacing:2px; margin:6px 0 2px 0; color:{color}; }}
      .row {{ display:flex; justify-content:space-between; gap:12px; font-size:17px; margin-top:6px; }}
      .row b {{ font-weight:700; }}
      .note {{ margin-top:10px; font-size:15px; color:#4E6A82; }}
      button {{ margin-top:14px; width:100%; height:56px; border:0; border-radius:8px; background:#41A8C4; color:#fff;
               font-size:20px; font-weight:700; cursor:pointer; }}
      button:hover {{ background:#2B869F; }}
      @media print {{ button {{ display:none; }} .ticket {{ border:2px solid #000; }} }}
    </style>
    <div class="ticket">
      <div class="top"><span>PPUM · {t["ticket"]}</span><span>{res["stamp"]}</span></div>
      <div class="num">{res["ticket"]}</div>
      <div class="row"><span>{t["zone"]}: <b>{zt["zone"]}</b></span><span>{t["wait"]}: <b>{zt["wait"]}</b></span></div>
      <div class="row"><span>{t["name"]}: <b>{who}</b></span><span><b>{info}</b></span></div>
      <div class="note">{t["show_nurse"]}</div>
    </div>
    <button onclick="window.print()">{t["print"]}</button>
    """, height=310)

    st.button(t["new"], on_click=new_patient, use_container_width=True, key="new_patient_btn")

# ------------------------------------------------------------------
# BOTTOM BAR
# ------------------------------------------------------------------
st.markdown(f'<div class="footer-note">{t["footer"]}</div>', unsafe_allow_html=True)