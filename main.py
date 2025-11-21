import streamlit as st
from crew import WarRoomCrew
from utils import identify_roles
from pypdf import PdfReader

# --- Page Config ---
st.set_page_config(
    page_title="The War Room",
    page_icon="⚖️",
    layout="wide"
)

# --- CSS (FIXED) ---
st.markdown("""
<style>
    /* Force text color to black for these light-colored boxes to fix Dark Mode visibility issues */
    .shark-box { border-left: 5px solid #ff4b4b; padding: 10px; background-color: #ffecec; color: black !important; }
    .shield-box { border-left: 5px solid #4b7bff; padding: 10px; background-color: #ecf2ff; color: black !important; }
    .mediator-box { border-left: 5px solid #21c354; padding: 20px; background-color: #f0fff4; color: black !important; }
    
    /* FIX: Added 'color: black !important' to ensure visibility on the light gray background */
    .role-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 20px; color: black !important; }
    
    .role-card h4 { color: black !important; margin: 0 0 10px 0; }
    .role-card p { margin: 5px 0; }
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

# Sidebar
with st.sidebar:
    st.header("📁 Upload Case")
    uploaded_file = st.file_uploader("Select Contract (PDF)", type=['pdf'])
    
    st.markdown("---")
    st.caption("⚡ **System Stats**")
    st.caption("Model: GPT-4o-mini")
    st.caption("Est. Cost per Run: < $0.01")

# Main Logic
if uploaded_file:
    # 1. Extract Text
    with st.spinner("📖 Reading document..."):
        contract_text = get_pdf_text(uploaded_file)

    if contract_text:
        # 2. AUTO-DETECT ROLES
        if 'roles' not in st.session_state:
            with st.spinner("🔍 Analyzing Parties & Roles..."):
                st.session_state['roles'] = identify_roles(contract_text)
        
        roles = st.session_state['roles']

        # Show the Analysis Card (Now readable!)
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
                    # Initialize Crew
                    war_room = WarRoomCrew(
                        contract_text[:5000], 
                        user_role=roles['user_role'],
                        counter_party=roles['counter_party']
                    )
                    
                    # Run Simulation
                    result_object = war_room.run()
                    
                    # FIX: Convert CrewOutput object to string explicitly
                    final_result = str(result_object)
                    
                    st.success("Negotiation Complete!")
                    
                    # Display Verdict
                    st.markdown("### 🏛️ The Final Verdict")
                    st.markdown(f'<div class="mediator-box">{final_result}</div>', unsafe_allow_html=True)
                    
                    # Download Button (Now works because we use the string version)
                    st.download_button(
                        label="📥 Download Legal Verdict",
                        data=final_result,
                        file_name="War_Room_Verdict.md",
                        mime="text/markdown"
                    )
                    
                    with st.expander("View Agent Debate Logs"):
                        st.info("To see the full back-and-forth debate between the Shark and Shield, check your terminal logs!")

                except Exception as e:
                    st.error(f"Simulation failed: {e}")