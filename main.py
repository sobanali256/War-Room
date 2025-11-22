import streamlit as st
import time
import re
from pypdf import PdfReader
from fpdf import FPDF

# --- BACKEND IMPORTS ---
try:
    from crew import WarRoomCrew
    from utils import analyze_contract
except ImportError:
    st.error("⚠️ Critical Error: 'crew.py' or 'utils.py' not found. Please ensure backend files are in the directory.")
    st.stop()

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="The War Room",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS STYLING ---
st.markdown("""
<style>
    /* Global Settings */
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    
    /* Card Styling */
    .st-card { border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 6px 10px rgba(0,0,0,0.3); }
    
    /* Agent Specific Cards */
    .shark-card { background: linear-gradient(145deg, #2b1111, #1a0b0b); border-left: 6px solid #ff4b4b; color: #f2c6c6; }
    .shield-card { background: linear-gradient(145deg, #0b1221, #080d16); border-left: 6px solid #4b7bff; color: #c6d5f2; }
    .mediator-card { background: linear-gradient(145deg, #0f2615, #09140b); border: 2px solid #21c354; padding: 25px; color: #b8e6b8; }
    .negotiator-card { background: linear-gradient(145deg, #2d2d1d, #1f1f14); border-left: 6px solid #f1c40f; color: #f9e79f; }
    
    /* Role & Dashboard Badges */
    .role-badge { background-color: #262730; padding: 15px; border-radius: 10px; margin-bottom: 15px; font-weight: bold; font-size: 1.1em; text-align: center; border: 1px solid #444; }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #1c1f26;
        border-radius: 5px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #262730;
        border-bottom: 2px solid #4b7bff;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---

def clean_text(text):
    """Sanitizes LLM output to remove artifacts."""
    if not isinstance(text, str):
        return str(text)
    text = text.replace("undefined", "").replace("null", "")
    text = text.replace("```", "").replace("`", "")
    return text.strip()

def get_pdf_text(uploaded_file):
    """Extracts text from the uploaded PDF (limit 30 pages)."""
    text = ""
    try:
        pdf_reader = PdfReader(uploaded_file)
        for i, page in enumerate(pdf_reader.pages):
            if i >= 30: break # Increased limit
            text += page.extract_text()
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None
    return text

def create_pdf(text):
    """Generates a downloadable PDF of the verdict."""
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'The War Room - Legal Verdict', 0, 1, 'C')
            self.ln(10)
    
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    safe_text = clean_text(text).encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, safe_text)
    return pdf.output(dest='S').encode('latin-1')

# --- MAIN APP LAYOUT ---

st.title("⚖️ The War Room")
st.markdown("### AI Multi-Agent Contract Negotiation System")

# --- SIDEBAR ---
with st.sidebar:
    st.header("📁 Case Files")
    uploaded_file = st.file_uploader("Upload Contract (PDF)", type=['pdf'])
    
    st.divider()
    if st.button("🔄 Start New Negotiation", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- LOGIC CONTROLLER ---

if uploaded_file:
    # 1. TEXT EXTRACTION & ANALYSIS
    if 'contract_text' not in st.session_state:
        with st.spinner("🔍 Extracting Text & Analyzing Risks..."):
            text = get_pdf_text(uploaded_file)
            if text:
                st.session_state['contract_text'] = text
                
                # CALL BACKEND: Analyze Contract (Send first 10k chars for risk analysis)
                try:
                    analysis_result = analyze_contract(text[:10000]) 
                    st.session_state['roles'] = analysis_result.get('roles', {})
                    st.session_state['risk_scores'] = analysis_result.get('risk_scores', {})
                except Exception as e:
                    st.error(f"Backend Analysis Failed: {e}")
                    st.stop()
    
    # Ensure we have data before rendering
    if 'roles' in st.session_state and 'risk_scores' in st.session_state:
        roles = st.session_state['roles']
        scores = st.session_state['risk_scores']
        
        # --- RISK DASHBOARD ---
        st.markdown("### 📊 Risk Assessment")
        kpi1, kpi2, kpi3 = st.columns(3)
        
        def get_color(score):
            if score < 30: return "normal"
            if score < 70: return "off"
            return "inverse"
        
        l_score = scores.get('liability_score', 0)
        f_score = scores.get('financial_risk', 0)
        u_score = scores.get('unfairness_score', 0)

        kpi1.metric(label="Liability Exposure", value=f"{l_score}/100", delta="High" if l_score > 70 else "OK", delta_color=get_color(l_score))
        kpi2.metric(label="Financial Risk", value=f"{f_score}/100", delta="High" if f_score > 70 else "OK", delta_color=get_color(f_score))
        kpi3.metric(label="Unfairness Score", value=f"{u_score}/100", delta="High" if u_score > 70 else "OK", delta_color=get_color(u_score))
        
        st.warning(f"⚠️ **Key Red Flag:** {clean_text(scores.get('summary', 'Review required.'))}")
        st.divider()

        # --- ROLE DISPLAY ---
        c1, c2 = st.columns(2)
        user_name = roles.get('user_name', 'Client')
        counter_name = roles.get('counter_party_name', 'Counterparty')
        
        c1.markdown(f"<div class='role-badge'>🔵 <b>Us:</b> {user_name}</div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='role-badge'>🔴 <b>Them:</b> {counter_name}</div>", unsafe_allow_html=True)

        # 3. NEGOTIATION SIMULATION
        st.subheader("⚔️ The Negotiation Arena")
        
        if 'simulation_results' not in st.session_state:
            if st.button("🚀 Enter The Arena (Run AI Agents)", type="primary", use_container_width=True):
                with st.spinner("🧠 Agents are debating & drafting strategy..."):
                    try:
                        user_role = roles.get('user_role', 'Tenant')
                        counter_role = roles.get('counter_party', 'Landlord')
                        
                        # Initialize Crew with INCREASED Character Limit (25k)
                        war_room = WarRoomCrew(
                            st.session_state['contract_text'][:25000], 
                            user_role, 
                            counter_role
                        )
                        # Run Crew
                        result = war_room.run()
                        st.session_state['simulation_results'] = result
                        st.rerun()
                    except Exception as e:
                        st.error(f"Simulation Error: {e}")

        # 4. DISPLAY RESULTS (4 TABS)
        if 'simulation_results' in st.session_state:
            results = st.session_state['simulation_results']
            
            # Handle dictionary vs string output
            if isinstance(results, dict):
                shark_text = clean_text(results.get('shark_report', "No report generated."))
                shield_text = clean_text(results.get('shield_report', "No report generated."))
                verdict_text = clean_text(results.get('final_verdict', str(results)))
                negotiation_text = clean_text(results.get('negotiation_strategy', "No strategy generated."))
            else:
                shark_text = "See Mediator Verdict."
                shield_text = "See Mediator Verdict."
                verdict_text = clean_text(str(results))
                negotiation_text = "Strategy not available."

            # TABS Layout
            tab_shark, tab_shield, tab_mediator, tab_coach = st.tabs(["🦈 The Shark", "🛡️ The Shield", "⚖️ The Mediator", "🤝 The Coach"])

            with tab_shark:
                st.markdown("#### 🔴 Aggressive Strategy")
                st.markdown(f"<div class='st-card shark-card'>{shark_text}</div>", unsafe_allow_html=True)

            with tab_shield:
                st.markdown("#### 🔵 Defensive Strategy")
                st.markdown(f"<div class='st-card shield-card'>{shield_text}</div>", unsafe_allow_html=True)

            with tab_mediator:
                st.markdown("#### 🟢 Final Consensus")
                st.markdown(f"<div class='st-card mediator-card'>{verdict_text}</div>", unsafe_allow_html=True)
                st.divider()
                pdf_data = create_pdf(verdict_text)
                st.download_button(
                    label="📥 Download Final Verdict (PDF)",
                    data=pdf_data,
                    file_name="War_Room_Verdict.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            with tab_coach:
                st.markdown("#### 🤝 Negotiation Playbook")
                st.markdown(f"<div class='st-card negotiator-card'>{negotiation_text}</div>", unsafe_allow_html=True)

else:
    # Empty State
    st.markdown("""
    <div style='text-align: center; padding: 80px;'>
        <h1>Welcome to The War Room</h1>
        <p style='font-size: 1.2em;'>Upload a legal contract to initialize the Risk Dashboard and Agents.</p>
        <p style='color: #666;'>Supports PDF</p>
    </div>
    """, unsafe_allow_html=True)