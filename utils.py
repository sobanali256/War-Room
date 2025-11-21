from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import os
import json
from dotenv import load_dotenv

load_dotenv()

def identify_roles(contract_text):
    """
    Analyzes the contract text to identify the User (Shield) and the Opponent (Shark).
    Returns a dictionary with the roles.
    """
    
    # Use the cheap model for this quick check
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL_NAME"),
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0
    )

    prompt = PromptTemplate(
        template="""
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
        "{text_snippet}"

        Return ONLY a valid JSON object with these exact keys:
        {{
            "contract_type": "Type of contract (e.g. NDA, Lease)",
            "user_role": "The role of the vulnerable party (e.g. Freelancer)",
            "counter_party": "The role of the dominant party (e.g. Client)",
            "user_name": "Name of the vulnerable party (if found, else 'The Freelancer')",
            "counter_party_name": "Name of the dominant party (if found, else 'The Client')"
        }}
        """,
        input_variables=["text_snippet"]
    )

    # We only need the first 2000 chars to find the names
    chain = prompt | llm
    response = chain.invoke({"text_snippet": contract_text[:2000]})
    
    try:
        # Clean up potential markdown formatting from LLM response
        clean_json = response.content.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        # Fallback if extraction fails
        print(f"Error parsing roles: {e}")
        return {
            "contract_type": "General Agreement",
            "user_role": "Service Provider",
            "counter_party": "Client",
            "user_name": "You",
            "counter_party_name": "The Client"
        }