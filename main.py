import streamlit as st
from crew import WarRoomCrew
from utils import analyze_contract
from pypdf import PdfReader
from fpdf import FPDF

# --- Page Config ---
st.set_page_config(page_title="The War Room", page_icon="⚖️", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .st-card { border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .shark-card { background: linear-gradient(145deg, #2b1111, #1a0b0b); border-left: 4px solid #ff4b4b; color: #e0e0e0; }
    .shield-card { background: linear-gradient(145deg, #0b1221, #080d16); border-left: 4px solid #4b7bff; color: #e0e0e0; }
    .mediator-card { background: linear-gradient(145deg, #0f2615, #09140b); border: 1px solid #21c354; padding: 25px; color: #ffffff; }
    .role-badge { background-color: #262730; padding: 10px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #4a4a4a; }
</style>
""", unsafe_allow_html=True)

# --- PDF Generator ---
def create_pdf(text):
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'The War Room - Legal Verdict', 0, 1, 'C')
            self.ln(10)
    
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    safe_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, safe_text)
    return pdf.output(dest='S').encode('latin-1')

# --- Helper: PDF Text Extraction ---
def get_pdf_text(uploaded_file):
    text = ""
    try:
        pdf_reader = PdfReader(uploaded_file)
        for i, page in enumerate(pdf_reader.pages):
            if i >= 5: break 
            text += page.extract_text()
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None
    return text

# --- MAIN UI ---
st.title("⚖️ The War Room")
st.caption("Autonomous Multi-Agent Contract Defense System")

# Sidebar
with st.sidebar:
    st.header("📁 Case Files")
    uploaded_file = st.file_uploader("Upload Contract (PDF)", type=['pdf'])
    st.markdown("---")
    st.caption("⚡ Model: GPT-4o-mini")
    
    if st.button("🔄 Reset Simulation"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Main Logic
if uploaded_file:
    # 1. Analysis Phase
    if 'roles' not in st.session_state:
        with st.spinner("🔍 Analyzing Roles & Risk Profile..."):
            contract_text = get_pdf_text(uploaded_file)
            st.session_state['contract_text'] = contract_text
            
            analysis_result = analyze_contract(contract_text)
            st.session_state['roles'] = analysis_result['roles']
            st.session_state['risk_scores'] = analysis_result['risk_scores']
    
    roles = st.session_state['roles']
    scores = st.session_state['risk_scores']

    # --- RISK DASHBOARD ---
    st.markdown("### 📊 Risk Assessment")
    kpi1, kpi2, kpi3 = st.columns(3)
    
    def get_color(score):
        if score < 30: return "normal"
        if score < 70: return "off"
        return "inverse"
    
    kpi1.metric(label="Liability Exposure", value=f"{scores['liability_score']}/100", delta_color=get_color(scores['liability_score']))
    kpi2.metric(label="Financial Risk", value=f"{scores['financial_risk']}/100", delta_color=get_color(scores['financial_risk']))
    kpi3.metric(label="Unfairness Score", value=f"{scores['unfairness_score']}/100", delta_color=get_color(scores['unfairness_score']))
    st.warning(f"⚠️ **Key Red Flag:** {scores['summary']}")
    st.divider()

    # --- ROLE DISPLAY ---
    c1, c2 = st.columns(2)
    c1.markdown(f"<div class='role-badge'>🔵 <b>Us:</b> {roles['user_name']}</div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='role-badge'>🔴 <b>Them:</b> {roles['counter_party_name']}</div>", unsafe_allow_html=True)

    # 2. Run Simulation
    if 'simulation_results' not in st.session_state:
        if st.button("⚔️ Enter The Arena", type="primary", use_container_width=True):
            with st.spinner("⚔️ Agents are debating... (This takes ~45s)"):
                try:
                    war_room = WarRoomCrew(
                        st.session_state['contract_text'][:5000], 
                        roles['user_role'], 
                        roles['counter_party']
                    )
                    st.session_state['simulation_results'] = war_room.run()
                    st.rerun()
                except Exception as e:
                    st.error(f"Simulation Failed: {e}")

    # 3. Display Results
    if 'simulation_results' in st.session_state:
        results = st.session_state['simulation_results']
        
        # Sanitization
        shark_text = str(results['shark_report']).replace("undefined", "").strip()
        shield_text = str(results['shield_report']).replace("undefined", "").strip()
        verdict_text = str(results['final_verdict']).replace("undefined", "").strip()
        
        # The Debate
        st.markdown("### 🗣️ The Debate")
        col_shark, col_shield = st.columns(2)
        with col_shark:
            st.markdown(f"#### 🦈 The Shark")
            st.markdown(f"<div class='st-card shark-card'>{shark_text}</div>", unsafe_allow_html=True)
        with col_shield:
            st.markdown(f"#### 🛡️ The Shield")
            st.markdown(f"<div class='st-card shield-card'>{shield_text}</div>", unsafe_allow_html=True)

        # The Verdict
        st.divider()
        st.markdown("### 🏛️ Final Verdict")
        st.markdown(f"<div class='mediator-box mediator-card'>{verdict_text}</div>", unsafe_allow_html=True)

        # PDF Download
        pdf_data = create_pdf(verdict_text)
        st.download_button(
            label="📥 Download PDF Verdict",
            data=pdf_data,
            file_name="War_Room_Verdict.pdf",
            mime="application/pdf"
        )