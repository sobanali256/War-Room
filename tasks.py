from crewai import Task
import os

class WarRoomTasks:
    
    def attack_task(self, agent, contract_text, counter_party):
        return Task(
            description=f"""Analyze the following contract text with the mindset of a high-pressure corporate negotiator representing {counter_party}:
            '{contract_text}'
            
            Your objectives:
            1. Analyze language for vulnerabilities, vague wording, or exploitable gaps.
            2. Identify opportunities to shift liabilities away from {counter_party}.
            3. Draft a 'Red Report' that pushes for broadened indemnities and loosened obligations for your side.
            4. Frame adversarial arguments to weaken any existing protections for the other party.
            """,
            agent=agent,
            expected_output=f"A markdown 'Red Report' detailing aggressive demands, exploitable gaps, and strategic leverage points favoring {counter_party}.",
            output_file=os.path.join(os.getcwd(), "shark_output.md")
        )

    def defense_task(self, agent, contract_text, context, user_role):
        return Task(
            description=f"""Review the contract: '{contract_text}'
            AND the 'Red Report' provided by The Shark.
            
            Your objectives:
            1. Identify hidden threats and ambiguous obligations that harm {user_role}.
            2. Challenge the Shark's aggressive clauses with reasoned counterpositions.
            3. Propose strong protective alternatives (limiting liability, securing safeguards).
            4. Ensure {user_role} is not placed in a vulnerable position.
            """,
            agent=agent,
            context=context,
            expected_output=f"A markdown 'Blue Report' containing risk mitigation strategies, strong protective clauses, and a defense against the Shark's claims for {user_role}.",
            output_file=os.path.join(os.getcwd(), "shield_output.md")
        )

    def verdict_task(self, agent, contract_text, context):
        return Task(
            description=f"""Review the original contract, the Shark's Red Report, and the Shield's Blue Report.
            
            Your objectives:
            1. Filter out the extremes from both sides (Shark's aggression vs Shield's over-caution).
            2. Determine which arguments are legally valid and commercially reasonable.
            3. Draft a final version that creates a fair, market-standard structure.
            4. Ensure the final clauses withstand legal scrutiny and practical application.
           IMPORTANT FINAL STEP:
            For EVERY clause you rewrote or modified, you must provide a structured comparison at the very bottom of your report. 
            Use the exact format below for EACH clause:
            
            ---CLAUSE_COMPARISON_START---
            ORIGINAL: [Insert the exact original text of the clause]
            REVISED: [Insert your new fair version]
            EXPLANATION: [One sentence explaining why you changed it]
            ---CLAUSE_COMPARISON_END---
            
            (Repeat this block for as many clauses as you modified).
            """,
            agent=agent,
            context=context,
            expected_output="A Final Verdict + A strict Original vs Revised comparison block at the end explaining the compromise and providing the specific, rewritten contract clauses that represent the optimal midpoint.",
            output_file=os.path.join(os.getcwd(), "verdict_output.md")
        )
    
    def negotiation_task(self, agent, context, user_role, counter_party):
        return Task(
            description=f"""
            Review the 'Final Verdict' provided by the Mediator.
            Your goal is to prepare {user_role} to negotiate these terms with {counter_party}.
            
            Create a 'Negotiation Playbook' that includes:
            1. **The BATNA Assessment**: Estimate the Best Alternative to a Negotiated Agreement for both sides. 
               (e.g., "If they walk away, they lose X...").
            2. **The 'Ask' Script**: Specific, professional phrasing for how {user_role} should propose the new clauses 
               without sounding aggressive.
            3. **Objection Handling**: Anticipate the 3 most likely complaints {counter_party} will have. 
               Write out exact "Counter-Scripts" for {user_role} to use in response.
            4. **The 'Give-Get' Strategy**: Identify 'Throwaway Clauses' (things we can concede) to protect the 'Must-Haves'.
            """,
            agent=agent,
            context=context, # This passes the Mediator's Verdict to this task
            expected_output="A Markdown-formatted Negotiation Playbook containing scripts, BATNA analysis, and rebuttal strategies.",
            output_file=os.path.join(os.getcwd(), "negotiation_output.md")
        )
    
