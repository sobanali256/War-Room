from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import os
import difflib
import json
from dotenv import load_dotenv

load_dotenv()

def analyze_contract(contract_text):
    """
    Combines Role Identification AND Risk Assessment into a single API call 
    to save tokens and reduce latency.
    """
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL_NAME"),
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0
    )
    
    prompt = PromptTemplate(
        template="""
        You are a Legal AI Specialist. Perform two tasks simultaneously on the contract text provided inside <contract> tags.

        ---
        TASK 1: IDENTIFY ROLES
        We represent the "Vulnerable Party" (The Shield). The counter-party is the "Dominant Party" (The Shark).
        Rules:
        - Freelance: User=Freelancer, Counter=Client
        - Lease: User=Tenant, Counter=Landlord
        - NDA: User=Receiving Party, Counter=Disclosing Party
        - Employment: User=Employee, Counter=Employer
        - Generic: User=Service Provider, Counter=Customer

        TASK 2: ASSESS RISK
        Rate the contract on a scale of 0 (Safe) to 100 (Dangerous) for Liability, Financial Risk, and Unfairness.
        ---

        <contract>
        {text_snippet}
        </contract>

        Return ONLY a valid JSON object with this exact structure:
        {{
            "roles": {{
                "contract_type": "Type (e.g. NDA)",
                "user_role": "Role of vulnerable party",
                "counter_party": "Role of dominant party",
                "user_name": "Name of vulnerable party (or 'The User')",
                "counter_party_name": "Name of dominant party (or 'The Counterparty')"
            }},
            "risk_scores": {{
                "liability_score": 0-100,
                "financial_risk": 0-100,
                "unfairness_score": 0-100,
                "summary": "1 short sentence explaining the biggest red flag"
            }}
        }}
        """,
        input_variables=["text_snippet"]
    )
    
    # Process first 3000 characters
    chain = prompt | llm
    response = chain.invoke({"text_snippet": contract_text[:10000]})
    
    # Default Safe Fallback
    default_response = {
        "roles": {
            "contract_type": "General Agreement",
            "user_role": "Service Provider", 
            "counter_party": "Client",
            "user_name": "The User", 
            "counter_party_name": "The Counterparty"
        },
        "risk_scores": {
            "liability_score": 50, 
            "financial_risk": 50, 
            "unfairness_score": 50, 
            "summary": "Could not analyze risks."
        }
    }

    try:
        clean_json = response.content.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"JSON Parsing Error: {e}")
        return default_response
    

def get_redline_html(original_text, revised_text):
    """
    Generates a 'Track Changes' style HTML visualization.
    - Deleted words: Red strikethrough
    - Added words: Green bold
    """
    # Split into words for granular comparison
    a = original_text.split()
    b = revised_text.split()
    
    matcher = difflib.SequenceMatcher(None, a, b)
    html_output = []

    for opcode, a0, a1, b0, b1 in matcher.get_opcodes():
        if opcode == 'equal':
            # No change: just append the words
            html_output.append(" ".join(a[a0:a1]))
        elif opcode == 'insert':
            # Addition: Green background/text
            added_text = " ".join(b[b0:b1])
            html_output.append(f"<span style='color: #4caf50; background-color: #1b3320; font-weight: bold; padding: 2px 4px; border-radius: 4px;'>{added_text}</span>")
        elif opcode == 'delete':
            # Deletion: Red strikethrough
            deleted_text = " ".join(a[a0:a1])
            html_output.append(f"<span style='color: #ff4b4b; text-decoration: line-through; background-color: #331b1b; opacity: 0.8; padding: 2px 4px;'>{deleted_text}</span>")
        elif opcode == 'replace':
            # Replacement: Show deletion then addition
            deleted_text = " ".join(a[a0:a1])
            added_text = " ".join(b[b0:b1])
            html_output.append(f"<span style='color: #ff4b4b; text-decoration: line-through; background-color: #331b1b; opacity: 0.8; padding: 2px 4px;'>{deleted_text}</span>")
            html_output.append(f"<span style='color: #4caf50; background-color: #1b3320; font-weight: bold; padding: 2px 4px; border-radius: 4px;'>{added_text}</span>")
            
    return " ".join(html_output)