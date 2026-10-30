# user_interface.py
import streamlit as st
import datetime

# Configure the page layout
st.set_page_config(page_title="PPUM Smart Triage Kiosk", page_icon="🏥", layout="centered")

# --- CUSTOM CSS FOR BIGGER, PRETTIER KIOSK UI ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fbfd; }
    .kiosk-header {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border-top: 8px solid #1a4f7c;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 30px;
        text-align: center;
    }
    .kiosk-header h1 {
        color: #1a4f7c !important;
        font-family: 'Arial', sans-serif;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 5px;
    }
    .alert-card {
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .red-zone { background-color: #fff0f0; border: 4px solid #ff4b4b; }
    .red-zone h1 { color: #d32f2f !important; font-size: 3rem !important; font-weight: 900; margin-bottom: 10px; }
    .red-zone h3 { color: #b71c1c !important; font-size: 1.8rem; }
    
    .yellow-zone { background-color: #fffde7; border: 4px solid #fbc02d; }
    .yellow-zone h1 { color: #f57f17 !important; font-size: 3rem !important; font-weight: 900; margin-bottom: 10px; }
    .yellow-zone h3 { color: #f57f17 !important; font-size: 1.8rem; }
    
    .green-zone { background-color: #f1f8e9; border: 4px solid #689f38; }
    .green-zone h1 { color: #33691e !important; font-size: 3rem !important; font-weight: 900; margin-bottom: 10px; }
    .green-zone h3 { color: #558b2f !important; font-size: 1.8rem; }
    </style>
""", unsafe_allow_html=True)

# --- HOSPITAL BANNER & HEADER ---
st.markdown("""
    <div class="kiosk-header">
        <h1>🏥 Pusat Perubatan Universiti Malaya (PPUM)</h1>
        <h3 style="color: #4a4a4a; margin-top: 0;">Smart Triage Receptionist</h3>
        <p style="color: #777; font-size: 1.1rem;">Jabatan Perubatan Kecemasan</p>
    </div>
""", unsafe_allow_html=True)

# --- SECTION 1: DEMOGRAPHICS (NAMA, UMUR, JANTINA, TARIKH, MASA) ---
st.write("### 🧑‍⚕️ 1. Patient Details (Maklumat Pesakit)")
col1, col2 = st.columns(2)
with col1:
    patient_name = st.text_input("Name (Nama)", placeholder="Enter full name")
    age = st.number_input("Age (Umur)", min_value=1, max_value=120, value=25)
    date_visit = st.date_input("Date (Tarikh)", datetime.date.today())
with col2:
    gender = st.selectbox("Gender (Jantina)", ["Male (L)", "Female (P)", "Other"])
    time_visit = st.time_input("Time (Masa)", datetime.datetime.now().time())

# --- SECTION 2: REFERRAL (KES RUJUKAN) ---
st.write("### 📁 2. Referral Status (Status Rujukan)")
col_ref1, col_ref2 = st.columns(2)
with col_ref1:
    is_referred = st.radio("Referred Case? (Kes Rujukan?)", ["No (Tidak)", "Yes (Ya)"])
with col_ref2:
    if is_referred == "Yes (Ya)":
        referral_source = st.text_input("Referred As (Rujukan Sebagai)", placeholder="e.g., Klinik Kesihatan")

# --- SECTION 3: CHIEF COMPLAINT (ADUAN UTAMA) ---
st.write("### 📝 3. Chief Complaint (Aduan Utama Kesihatan)")
symptoms = st.text_area(
    "Describe your main symptoms (Nyatakan aduan utama anda):",
    placeholder="e.g., I have severe chest pain and I am sweating...",
    height=120
)
history = st.text_input("Past Medical History (Optional)", placeholder="e.g., Asthma, Diabetes")

# --- SECTION 4: VITALS & EXAM (TANDA VITAL & DAPATAN PEMERIKSAAN) ---
# Hidden behind an expander since walk-in patients usually don't enter this themselves
with st.expander("🩺 Clinical Vitals (Tanda Vital) - For Staff/Triage Use Only"):
    st.markdown("**Keadaan Am Pesakit (General Condition)**")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        conscious = st.radio("Conscious (Sedar Diri)?", ["Yes (Ya)", "No (Tidak)"])
    with col_g2:
        gcs_score = st.text_input("GCS Score", placeholder="e.g., 15")
        
    st.markdown("**Tanda Vital (Vital Signs)**")
    v1, v2, v3 = st.columns(3)
    with v1:
        pulse = st.text_input("Pulse (Kadar Nadi)", placeholder="bpm")
        resp_rate = st.text_input("Resp. Rate (Kadar Pernafasan)", placeholder="breaths/min")
    with v2:
        bp = st.text_input("BP (Tekanan Darah)", placeholder="mmHg")
        spo2 = st.text_input("SpO2", placeholder="%")
    with v3:
        temp = st.text_input("Temp (Suhu Badan)", placeholder="°C")
        pain_scale = st.selectbox("Pain Scale (Skala Kesakitan)", [str(i) for i in range(11)])
        
    exam_findings = st.text_area("Examination Findings (Dapatan Pemeriksaan)")

# --- PROCESS LOGIC ---
if st.button("Submit for Al Routing (Hantar untuk Saringan)", type="primary", use_container_width=True):
    st.markdown("---")
    
    user_input = symptoms.strip().lower()
    
    # GUARDRAIL: INCOMPLETE INFO
    if not user_input:
        st.warning("⚠️ **Input Error:** Please enter the chief complaint (Sila masukkan aduan utama).")
    else:
        # RED ZONE MOCK LOGIC
        if "chest pain" in user_input or "sweating" in user_input or conscious == "No (Tidak)":
            st.markdown("""
            <div class="alert-card red-zone">
                <h1>🚨 RED ZONE (ZON MERAH)</h1>
                <h3>CRITICAL / RESUSCITATION</h3>
                <br>
                <p><strong>Status:</strong> Critical Symptoms Detected</p>
                <p><strong>Wait Time:</strong> IMMEDIATE CARE</p>
                <hr style="border-top: 2px solid #ff4b4b;">
                <p style="font-size: 1.6rem; font-weight: 800;">👉 Proceed IMMEDIATELY to the Resuscitation Bay.</p>
            </div>
            """, unsafe_allow_html=True)
            
        # GREEN ZONE MOCK LOGIC
        elif "sore throat" in user_input or "runny nose" in user_input:
            st.markdown("""
            <div class="alert-card green-zone">
                <h1>🟢 GREEN ZONE (ZON HIJAU)</h1>
                <h3>NON-CRITICAL / OUTPATIENT</h3>
                <br>
                <p><strong>Status:</strong> Stable, Ambulatory</p>
                <p><strong>Wait Time:</strong> 60 - 120 Minutes</p>
                <hr style="border-top: 2px solid #689f38;">
                <p style="font-size: 1.6rem; font-weight: 800;">👉 Proceed to the Standard Outpatient Clinic Waiting Area.</p>
            </div>
            """, unsafe_allow_html=True)
            
        # YELLOW ZONE MOCK LOGIC
        else:
            st.markdown("""
            <div class="alert-card yellow-zone">
                <h1>🟡 YELLOW ZONE (ZON KUNING)</h1>
                <h3>SEMI-CRITICAL / URGENT</h3>
                <br>
                <p><strong>Status:</strong> Further Assessment Required</p>
                <p><strong>Wait Time:</strong> Within 30 Minutes</p>
                <hr style="border-top: 2px solid #fbc02d;">
                <p style="font-size: 1.6rem; font-weight: 800;">👉 Proceed to the Primary Triage Counter.</p>
            </div>
            """, unsafe_allow_html=True)