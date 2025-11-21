import streamlit as st
from crew import WarRoomCrew
from utils import identify_roles
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
    .role-badge { background-color: #262730; padding: 10px; border-radius: 8px; margin-bottom: 15px; }
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
    
    # Sanitize text (remove emojis/complex chars that break basic PDFs)
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

# Sidebar
with st.sidebar:
    st.header("📁 Case Files")
    uploaded_file = st.file_uploader("Upload Contract (PDF)", type=['pdf'])
    st.caption("⚡ Model: GPT-4o-mini")

    # Reset Button (To clear history)
    if st.button("🔄 Reset Simulation"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Main Logic
if uploaded_file:
    # 1. Role Detection (Cached)
    if 'roles' not in st.session_state:
        with st.spinner("🔍 Analyzing Roles..."):
            contract_text = get_pdf_text(uploaded_file)
            st.session_state['roles'] = identify_roles(contract_text)
            st.session_state['contract_text'] = contract_text
    
    roles = st.session_state['roles']
    
    # Show Roles
    c1, c2 = st.columns(2)
    c1.markdown(f"<div class='role-badge'>🔵 <b>Us:</b> {roles['user_name']}</div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='role-badge'>🔴 <b>Them:</b> {roles['counter_party_name']}</div>", unsafe_allow_html=True)

    # 2. Run Simulation (Only if not already run)
    if 'simulation_results' not in st.session_state:
        if st.button("⚔️ Enter The Arena", type="primary", use_container_width=True):
            with st.spinner("⚔️ Agents are debating..."):
                try:
                    war_room = WarRoomCrew(
                        st.session_state['contract_text'][:5000], 
                        roles['user_role'], 
                        roles['counter_party']
                    )
                    # Save results to Session State
                    st.session_state['simulation_results'] = war_room.run()
                    st.rerun() # Force refresh to show results
                except Exception as e:
                    st.error(f"Failed: {e}")

    # 3. Display Results (From Session State)
    if 'simulation_results' in st.session_state:
        results = st.session_state['simulation_results']
        
        st.markdown("### 🗣️ The Debate")
        col_shark, col_shield = st.columns(2)
        with col_shark:
            st.markdown(f"#### 🦈 The Shark")
            st.markdown(f"<div class='st-card shark-card'>{results['shark_report']}</div>", unsafe_allow_html=True)
        with col_shield:
            st.markdown(f"#### 🛡️ The Shield")
            st.markdown(f"<div class='st-card shield-card'>{results['shield_report']}</div>", unsafe_allow_html=True)

        st.divider()
        st.markdown("### 🏛️ Final Verdict")
        st.markdown(f"<div class='mediator-box mediator-card'>{results['final_verdict']}</div>", unsafe_allow_html=True)

        # 4. PDF Download Button
        pdf_data = create_pdf(results['final_verdict'])
        
        st.download_button(
            label="📥 Download PDF Verdict",
            data=pdf_data,
            file_name="War_Room_Verdict.pdf",
            mime="application/pdf"
        )