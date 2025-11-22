import streamlit as st
from crew import WarRoomCrew
from utils import identify_roles
from pypdf import PdfReader
from fpdf import FPDF
import time

# --- Page Config ---
st.set_page_config(page_title="The War Room", page_icon="⚖️", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .st-card { border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 6px 10px rgba(0,0,0,0.3); }
    .shark-card { background: linear-gradient(145deg, #2b1111, #1a0b0b); border-left: 6px solid #ff4b4b; color: #f2c6c6; }
    .shield-card { background: linear-gradient(145deg, #0b1221, #080d16); border-left: 6px solid #4b7bff; color: #c6d5f2; }
    .mediator-card { background: linear-gradient(145deg, #0f2615, #09140b); border: 2px solid #21c354; padding: 25px; color: #b8e6b8; }
    .role-badge { background-color: #262730; padding: 10px; border-radius: 8px; margin-bottom: 15px; font-weight: bold; font-size: 1.1em; }
    .agent-title { font-size: 1.5em; font-weight: 700; margin-bottom: 10px; }
    .working-indicator {
        background: #21c354;
        color: black;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85em;
        display: inline-block;
        margin-bottom: 10px;
        box-shadow: 0 0 8px #21c354;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    .pdf-button {
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- PDF Generator ---
def create_pdf(text):
    from fpdf import FPDF
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

# --- Dummy Data ---
DUMMY_ROLES = {
    "contract_type": "Lease",
    "user_role": "Tenant",
    "counter_party": "Landlord",
    "user_name": "Alice",
    "counter_party_name": "Bob"
}

# Multi-turn mock debate messages for each agent
MOCK_DEBATE = {
    "shark": [
        {"role": "shark", "content": "Let's begin. The rent escalation clause is too aggressive."},
        {"role": "shield", "content": "We believe the escalation is fair given market rates."},
        {"role": "shark", "content": "But the annual increase exceeds the local average."},
        {"role": "shield", "content": "We can consider capping the increase at 5%."},
        {"role": "shark", "content": "Agreed, but also request a longer grace period for late payments."},
        {"role": "shield", "content": "A 10-day grace period is acceptable."}
    ],
    "shield": [
        {"role": "shield", "content": "We want to ensure the tenant's rights are protected."},
        {"role": "shark", "content": "The landlord also needs timely payments."},
        {"role": "shield", "content": "We propose a 10-day grace period for late rent."},
        {"role": "shark", "content": "That is reasonable. Let's also clarify maintenance responsibilities."},
        {"role": "shield", "content": "Tenant will handle minor repairs, landlord covers major ones."},
        {"role": "shark", "content": "Accepted."}
    ],
    "mediator": [
        {"role": "mediator", "content": "Welcome to the negotiation. Let's keep it constructive."},
        {"role": "mediator", "content": "Both parties have valid points on rent escalation."},
        {"role": "mediator", "content": "A 5% cap and 10-day grace period seem fair."},
        {"role": "mediator", "content": "Maintenance split as discussed is standard practice."},
        {"role": "mediator", "content": "Agreement reached. Please review the final contract draft."}
    ]
}

DUMMY_SIM_RESULTS = {
    "shark_report": "🦈 Dummy Shark report: Aggressive points made.",
    "shield_report": "🛡️ Dummy Shield report: Protective arguments highlighted.",
    "final_verdict": "⚖️ Dummy Mediator verdict: Balanced, fair contract clause."
}

# --- Mock Step-by-Step Negotiation Generator ---
def generate_mock_turn_based_negotiation(rounds=4):
    mediator_msgs = []
    shark_msgs = []
    shield_msgs = []

    mediator_openings = [
        "Welcome to the negotiation. Let's aim for a fair agreement.",
        "Let's discuss the rent escalation clause.",
        "Now, let's address the maintenance responsibilities.",
        "Let's ensure both parties are comfortable with the terms.",
        "Final thoughts before we conclude?"
    ]
    shark_responses = [
        "The proposed escalation is too high for the current market.",
        "I believe the tenant should handle minor repairs only.",
        "The grace period for late payments is too short.",
        "The landlord's responsibilities should be more clearly defined.",
        "I request a cap on annual increases."
    ]
    shield_responses = [
        "We are open to a reasonable cap, perhaps 5%.",
        "Tenant can handle minor repairs, but major ones should be on the landlord.",
        "A 10-day grace period is acceptable.",
        "We agree to clarify the landlord's duties.",
        "We appreciate the mediator's guidance."
    ]
    mediator_replies = [
        "A 5% cap and 10-day grace period seem fair.",
        "Splitting maintenance as discussed is standard.",
        "Both parties have shown flexibility.",
        "Let's finalize the agreement based on these terms.",
        "Thank you both for your cooperation."
    ]

    for i in range(rounds):
        m_msg = mediator_openings[i] if i < len(mediator_openings) else "Let's continue the discussion."
        mediator_msgs.append({"role": "mediator", "content": m_msg})
        s_msg = shark_responses[i] if i < len(shark_responses) else "No further objections from my side."
        shark_msgs.append({"role": "shark", "content": s_msg})
        sh_msg = shield_responses[i] if i < len(shield_responses) else "We are satisfied with the current terms."
        shield_msgs.append({"role": "shield", "content": sh_msg})
        mr_msg = mediator_replies[i] if i < len(mediator_replies) else "Let's proceed to finalize."
        mediator_msgs.append({"role": "mediator", "content": mr_msg})

    shark_report = "\n\n".join([m["content"] for m in shark_msgs])
    shield_report = "\n\n".join([m["content"] for m in shield_msgs])
    final_verdict = "\n\n".join([m["content"] for m in mediator_msgs])

    return {
        "shark_report": shark_report,
        "shield_report": shield_report,
        "final_verdict": final_verdict,
        "shark_messages": shark_msgs,
        "shield_messages": shield_msgs,
        "mediator_messages": mediator_msgs
    }

def generate_mock_verdict_only(rounds=4):
    mediator_msgs = []
    mediator_openings = [
        "Welcome to the negotiation. Let's aim for a fair agreement.",
        "Let's discuss the rent escalation clause.",
        "Now, let's address the maintenance responsibilities.",
        "Let's ensure both parties are comfortable with the terms.",
        "Final thoughts before we conclude?"
    ]
    mediator_replies = [
        "A 5% cap and 10-day grace period seem fair.",
        "Splitting maintenance as discussed is standard.",
        "Both parties have shown flexibility.",
        "Let's finalize the agreement based on these terms.",
        "Thank you both for your cooperation."
    ]
    for i in range(rounds):
        m_msg = mediator_openings[i] if i < len(mediator_openings) else "Let's continue the discussion."
        mediator_msgs.append({"role": "mediator", "content": m_msg})
        mr_msg = mediator_replies[i] if i < len(mediator_replies) else "Let's proceed to finalize."
        mediator_msgs.append({"role": "mediator", "content": mr_msg})
    final_verdict = "\n\n".join([m["content"] for m in mediator_msgs])
    return {
        "shark_report": "",
        "shield_report": "",
        "final_verdict": final_verdict,
        "shark_messages": [],
        "shield_messages": [],
        "mediator_messages": mediator_msgs
    }

def generate_mock_turns_for_ui(rounds=4):
    mediator_openings = [
        "Welcome to the negotiation. Let's aim for a fair agreement.",
        "Let's discuss the rent escalation clause.",
        "Now, let's address the maintenance responsibilities.",
        "Let's ensure both parties are comfortable with the terms.",
        "Final thoughts before we conclude?"
    ]
    shark_responses = [
        "The proposed escalation is too high for the current market.",
        "I believe the tenant should handle minor repairs only.",
        "The grace period for late payments is too short.",
        "The landlord's responsibilities should be more clearly defined.",
        "I request a cap on annual increases."
    ]
    shield_responses = [
        "We are open to a reasonable cap, perhaps 5%.",
        "Tenant can handle minor repairs, but major ones should be on the landlord.",
        "A 10-day grace period is acceptable.",
        "We agree to clarify the landlord's duties.",
        "We appreciate the mediator's guidance."
    ]
    mediator_replies = [
        "A 5% cap and 10-day grace period seem fair.",
        "Splitting maintenance as discussed is standard.",
        "Both parties have shown flexibility.",
        "Let's finalize the agreement based on these terms.",
        "Thank you both for your cooperation."
    ]
    turns = []
    for i in range(rounds):
        turns.append(("mediator", mediator_openings[i] if i < len(mediator_openings) else "Let's continue the discussion."))
        turns.append(("shark", shark_responses[i] if i < len(shark_responses) else "No further objections from my side."))
        turns.append(("shield", shield_responses[i] if i < len(shield_responses) else "We are satisfied with the current terms."))
        turns.append(("mediator", mediator_replies[i] if i < len(mediator_replies) else "Let's proceed to finalize."))
    # Final verdict (after all rounds)
    final_verdict = "\n\n".join([t[1] for t in turns if t[0] == "mediator"])
    return turns, final_verdict

# --- MAIN UI ---
st.title("⚖️ The War Room")

# Sidebar
with st.sidebar:
    st.header("📁 Case Files")
    uploaded_file = st.file_uploader("Upload Contract (PDF)", type=['pdf'])
    st.caption("⚡ Model: Gemini-2.0-flash / GPT-4o-mini")
    # Mock Mode Toggle (now supports step-by-step negotiation)
    mock_mode = st.checkbox(
        "🧪 Mock Step-by-Step Live Negotiation (UI test: live agent turns)",
        value=st.session_state.get("mock_mode", True)
    )
    if mock_mode != st.session_state.get("mock_mode", False):
        st.session_state["mock_mode"] = mock_mode
        for key in ["roles", "simulation_results", "simulation_running"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    if st.button("🔄 Reset Simulation"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Main Logic
if uploaded_file or st.session_state.get("mock_mode", False):
    # 1. Role Detection (Cached)
    if 'roles' not in st.session_state:
        if st.session_state.get("mock_mode", False):
            st.session_state['roles'] = DUMMY_ROLES.copy()
            st.session_state['contract_text'] = "Dummy contract text for mock mode."
        else:
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
            if st.session_state.get("mock_mode", False):
                st.session_state["simulation_running"] = True
                st.session_state["negotiation_turn"] = 0
                st.session_state["last_outputs"] = {"mediator": "", "shark": "", "shield": ""}
                st.session_state["final_verdict"] = ""
                st.rerun()
            else:
                with st.spinner("⚔️ Agents are debating..."):
                    try:
                        war_room = WarRoomCrew(
                            st.session_state['contract_text'][:5000], 
                            roles['user_role'], 
                            roles['counter_party']
                        )
                        # Save results to Session State
                        st.session_state['simulation_results'] = war_room.run()
                        st.rerun()  # Force refresh to show results
                    except Exception as e:
                        st.error(f"Failed: {e}")

    # Step-by-step live negotiation simulation
    if st.session_state.get("simulation_running", False) and st.session_state.get("mock_mode", False):
        turns, final_verdict = generate_mock_turns_for_ui(rounds=5)
        total_turns = len(turns)
        turn_idx = st.session_state.get("negotiation_turn", 0)
        last_outputs = st.session_state.get("last_outputs", {"mediator": "", "shark": "", "shield": ""})

        # Determine which agent is thinking now
        if turn_idx < total_turns:
            agent, msg = turns[turn_idx]
            # Show UI with spinner for current agent, last output for others
            col_shark, col_mediator, col_shield = st.columns(3)
            with col_shark:
                st.markdown("<div class='agent-title'>🦈 The Shark</div>", unsafe_allow_html=True)
                if agent == "shark":
                    st.markdown("<div class='working-indicator'>Working...</div>", unsafe_allow_html=True)
                elif last_outputs["shark"]:
                    st.markdown(f"<div class='st-card shark-card'>{last_outputs['shark']}</div>", unsafe_allow_html=True)
            with col_mediator:
                st.markdown("<div class='agent-title'>⚖️ The Mediator</div>", unsafe_allow_html=True)
                if agent == "mediator":
                    st.markdown("<div class='working-indicator'>Working...</div>", unsafe_allow_html=True)
                elif last_outputs["mediator"]:
                    st.markdown(f"<div class='st-card mediator-card'>{last_outputs['mediator']}</div>", unsafe_allow_html=True)
            with col_shield:
                st.markdown("<div class='agent-title'>🛡️ The Shield</div>", unsafe_allow_html=True)
                if agent == "shield":
                    st.markdown("<div class='working-indicator'>Working...</div>", unsafe_allow_html=True)
                elif last_outputs["shield"]:
                    st.markdown(f"<div class='st-card shield-card'>{last_outputs['shield']}</div>", unsafe_allow_html=True)
            # Simulate agent thinking
            time.sleep(1.1)
            # Update last_outputs for the agent that just finished
            last_outputs = last_outputs.copy()
            last_outputs[agent] = msg
            st.session_state["last_outputs"] = last_outputs
            st.session_state["negotiation_turn"] = turn_idx + 1
            # If this was the last turn, next rerun will show verdict
            st.rerun()
        else:
            # All turns done: show only final verdict in mediator, clear others
            st.session_state['simulation_results'] = {
                "shark_report": "",
                "shield_report": "",
                "final_verdict": final_verdict
            }
            st.session_state["simulation_running"] = False
            st.session_state["last_outputs"] = {"mediator": "", "shark": "", "shield": ""}
            st.session_state["negotiation_turn"] = 0
            st.rerun()

    # 3. Display Results (From Session State)
    if 'simulation_results' in st.session_state and not st.session_state.get("simulation_running", False):
        results = st.session_state['simulation_results']

        col_shark, col_mediator, col_shield = st.columns(3)

        with col_shark:
            st.markdown("<div class='agent-title'>🦈 The Shark</div>", unsafe_allow_html=True)
            # Empty after simulation
        with col_mediator:
            st.markdown("<div class='agent-title'>⚖️ The Mediator</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='st-card mediator-card'>{results.get('final_verdict','')}</div>", unsafe_allow_html=True)
        with col_shield:
            st.markdown("<div class='agent-title'>🛡️ The Shield</div>", unsafe_allow_html=True)
            # Empty after simulation

        st.divider()

        # 4. PDF Download Button (centered)
        pdf_text = results.get('final_verdict', '')

        pdf_data = create_pdf(pdf_text)
        st.download_button(
            label="📥 Download PDF Verdict",
            data=pdf_data,
            file_name="War_Room_Verdict.pdf",
            mime="application/pdf",
            help="Download the final negotiated contract summary as PDF",
            key="download_pdf"
        )

else:
    st.info("Please upload a contract PDF file to get started.")
