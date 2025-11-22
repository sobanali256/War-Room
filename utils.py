import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("Loaded key:", os.getenv("GEMINI_API_KEY"))


# Use a cheap, fast model for role-identification
MODEL = "gemini-2.0-flash"

def identify_roles(contract_text):
    """
    Identifies roles in the contract using Gemini.
    Returns a dictionary with detected parties & contract type.
    """

    prompt = f"""
You are a legal intake clerk. Read the start of this contract and extract the parties.

We are representing the "Vulnerable Party" (The Shield). 
The counter-party is the "Dominant Party" (The Shark).

Rules for extraction:
- If Freelance Contract: User = Freelancer, Opponent = Client
- If Lease: User = Tenant, Opponent = Landlord
- If NDA: User = Receiving Party, Opponent = Disclosing Party
- If Employment: User = Employee, Opponent = Employer
- If Generic: User = Service Provider, Opponent = Customer

Contract Text Snippet:
\"\"\"{contract_text[:2000]}\"\"\"

Return ONLY a valid JSON object with these exact keys:
{{
    "contract_type": "Type of contract (e.g. NDA, Lease)",
    "user_role": "The role of the vulnerable party",
    "counter_party": "The role of the dominant party",
    "user_name": "Name of the vulnerable party (if found, else 'The Freelancer')",
    "counter_party_name": "Name of the dominant party (if found, else 'The Client')"
}}
"""

    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)

        # Extract text directly
        raw = response.text.strip()

        # Remove markdown noise
        raw = raw.replace("```json", "").replace("```", "").strip()

        return json.loads(raw)

    except Exception as e:
        print(f"Gemini role extraction failed: {e}")
        return {
            "contract_type": "General Agreement",
            "user_role": "Service Provider",
            "counter_party": "Client",
            "user_name": "You",
            "counter_party_name": "The Client"
        }
