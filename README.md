# ⚖️ The War Room: Autonomous Multi-Agent Contract Negotiation

> **"The AlphaGo Moment for Legal Infrastructure"**
> A live, adversarial AI simulation where autonomous agents debate contract terms to protect freelancers, tenants, and employees.

![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue) ![CrewAI](https://img.shields.io/badge/CrewAI-Agentic_Framework-orange) ![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red)

## 📖 Overview
"The War Room" is an AI-powered legal defense system designed to solve the **"Sycophancy Problem"** in standard LLMs. Instead of asking a single AI to "review a contract" (which often yields generic, risk-averse advice), we orchestrate a **high-stakes debate** between three autonomous agents with conflicting goals.

The user simply uploads a PDF, and the system automatically detects their role (e.g., Tenant, Freelancer) and fights on their behalf.

## 🤖 The Crew (Agent Architecture)

The system utilizes **CrewAI** to manage a sequential adversarial process:

1.  🔴 **The Shark (Aggressor):** A ruthless corporate attorney engineered to maximize leverage for the opposing party. It hunts for loopholes and demands strict liability shifts.
2.  🔵 **The Shield (Defender):** Your personal legal guardian. It actively monitors the Shark's output, flagging hidden risks and proposing protective clauses to safeguard the user.
3.  🟢 **The Mediator (Judge):** A neutral arbiter that filters out the extremes from both sides to synthesize a fair, "Market Standard" agreement.

## ✨ Key Features
* **Zero-Touch Role Detection:** Automatically identifies if the contract is a Lease, NDA, or Employment Agreement and assigns the correct "Client" to the agents.
* **Adversarial Equilibrium:** Uses debate to force the AI to explore the extremes of a solution space before converging.
* **Cost-Efficient:** Optimized to run on `gpt-4o-mini`, making high-level legal reasoning accessible for pennies.
* **Split-Screen UI:** Built with Streamlit to visualize the "Battle" between agents in real-time.

## 🚀 Installation & Setup

**Prerequisites:** Python 3.10 or 3.11 (Python 3.13 is not supported).

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/your-username/the-war-room.git](https://github.com/your-username/the-war-room.git)
    cd the-war-room
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**
    Create a `.env` file in the root directory and add your OpenAI Key:
    ```ini
    OPENAI_API_KEY=sk-proj-your-key-here
    OPENAI_MODEL_NAME=gpt-4o-mini
    ```

## ⚔️ Usage

1.  Run the Streamlit application:
    ```bash
    streamlit run main.py
    ```
2.  The web interface will open at `http://localhost:8501`.
3.  Upload any PDF contract (NDA, Lease, Freelance Agreement).
4.  Watch the agents debate and receive your **Final Verdict**.

## 🛠️ Tech Stack
* **Orchestration:** [CrewAI](https://crewai.com) (Sequential Processes)
* **LLM:** GPT-4o-mini (via LangChain)
* **Interface:** Streamlit
* **Data Processing:** PyPDF

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

---
*Built for the [Hackathon Name] 2025.*
