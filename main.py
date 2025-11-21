import streamlit as st
from crew import WarRoomCrew
from utils import identify_roles # Import our new helper
import time
from pypdf import PdfReader

# --- Page Config ---
st.set_page_config(
    page_title="The War Room",
    page_icon="⚖️",
    layout="wide"
)

# --- CSS (Keep your styles) ---
st.markdown("""
<style>
    .shark-box { border-left: 5px solid #ff4b4b; padding: 10px; background-color: #ffecec; color: black; }
    .shield-box { border-left: 5px solid #4b7bff; padding: 10px; background-color: #ecf2ff; color: black; }
    .mediator-box { border-left: 5px solid #21c354; padding: 20px; background-color: #f0fff4; color: black; }
    .role-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- Helper: PDF Text Extraction ---
def get_pdf_text(uploaded_file):
    text = ""
    try:
        pdf_reader = PdfReader(uploaded_file)
        # Limit to first 5 pages for Hackathon speed
        for i, page in enumerate(pdf_reader.pages):
            if i >= 5: break 
            text += page.extract_text()
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None
    return text

# --- Main UI ---
st.title("⚖️ The War Room")
st.subheader("Just upload. We fight for you.")

# Sidebar is now simple
with st.sidebar:
    st.header("📁 Upload Case")
    uploaded_file = st.file_uploader("Select Contract (PDF)", type=['pdf'])
    
    st.markdown("---")
    st.info("ℹ️ The system automatically detects if you are the Freelancer, Tenant, or Employee.")

# Main Logic
if uploaded_file:
    # 1. Extract Text
    with st.spinner("📖 Reading document..."):
        contract_text = get_pdf_text(uploaded_file)

    if contract_text:
        # 2. AUTO-DETECT ROLES (The New Magic Step)
        if 'roles' not in st.session_state:
            with st.spinner("🔍 Analyzing Parties & Roles..."):
                st.session_state['roles'] = identify_roles(contract_text)
        
        roles = st.session_state['roles']

        # Show the user what we found (Confidence check)
        st.markdown(f"""
        <div class="role-card">
            <h4>📑 Analysis Detected: {roles['contract_type']}</h4>
            <p><b>🔵 We are protecting:</b> {roles['user_name']} ({roles['user_role']})</p>
            <p><b>🔴 We are fighting:</b> {roles['counter_party_name']} ({roles['counter_party']})</p>
        </div>
        """, unsafe_allow_html=True)

        start_btn = st.button("⚔️ Enter The War Room", type="primary")

        if start_btn:
            with st.spinner(f"⚔️ The Shark is reviewing {roles['user_name']}'s contract..."):
                try:
                    # Pass the DETECTED roles into the Crew
                    war_room = WarRoomCrew(
                        contract_text[:5000], 
                        user_role=roles['user_role'],
                        counter_party=roles['counter_party']
                    )
                    
                    final_result = war_room.run()
                    
                    st.success("Negotiation Complete!")
                    st.markdown("### 🏛️ The Final Verdict")
                    st.markdown(f'<div class="mediator-box">{final_result}</div>', unsafe_allow_html=True)
                    
                    # View the raw debate
                    with st.expander("View Agent Debate Logs"):
                        st.write("Full agent reasoning would be streamed here.")

                except Exception as e:
                    st.error(f"Simulation failed: {e}")