from crewai import Crew, Process
from agents import WarRoomAgents
from tasks import WarRoomTasks
import os

class WarRoomCrew:
    def __init__(self, contract_text, user_role="The User", counter_party="The Counterparty", aggression_mode="Professional"):
        self.contract_text = contract_text
        self.user_role = user_role
        self.counter_party = counter_party
        self.aggression_mode = aggression_mode  # <--- Store the slider value
        self.agents = WarRoomAgents()
        self.tasks = WarRoomTasks()

    def run(self):
        # 1. Init Agents
        # We pass the aggression_mode to the Shark here
        shark = self.agents.shark_agent(self.counter_party, self.aggression_mode)
        shield = self.agents.shield_agent(self.user_role)
        mediator = self.agents.mediator_agent()
        negotiator = self.agents.negotiator_agent()

        # 2. Init Tasks
        attack = self.tasks.attack_task(shark, self.contract_text, self.counter_party)
        defense = self.tasks.defense_task(shield, self.contract_text, [attack], self.user_role)
        verdict = self.tasks.verdict_task(mediator, self.contract_text, [attack, defense])
        negotiation = self.tasks.negotiation_task(negotiator, [verdict], self.user_role, self.counter_party)

        # 3. Run Crew
        crew = Crew(
            agents=[shark, shield, mediator, negotiator],
            tasks=[attack, defense, verdict, negotiation],
            process=Process.sequential,
            verbose=True
        )

        crew.kickoff()

        # 4. The "Source of Truth" Extractor
        def get_output(task_index, filename):
            # Priority 1: Grab from the finished Crew object (Most reliable)
            try:
                task_output = crew.tasks[task_index].output
                if hasattr(task_output, 'raw'):
                    return clean_garbage(task_output.raw)
                if hasattr(task_output, 'result'):
                    return clean_garbage(str(task_output.result))
            except Exception as e:
                print(f"Memory read failed for {filename}: {e}")

            # Priority 2: Read the File
            try:
                if os.path.exists(filename):
                    with open(filename, "r", encoding='utf-8') as f:
                        return clean_garbage(f.read())
            except Exception as e:
                print(f"File read failed for {filename}: {e}")

            return "⚠️ Simulation Error: Output not generated. Please check terminal logs."

        # 5. Garbage Cleaner
        def clean_garbage(text):
            text = str(text)
            if text.strip().startswith("description=") or "description='" in text:
                return "⚠️ Data Cleaning Error: The agent returned metadata instead of text. Check terminal for raw output."
            return text

        # Return using INDEX (0=Shark, 1=Shield, 2=Mediator, 3=Negotiator)
        return {
            "shark_report": get_output(0, "shark_output.md"),
            "shield_report": get_output(1, "shield_output.md"),
            "final_verdict": get_output(2, "verdict_output.md"),
            "negotiation_strategy": get_output(3, "negotiation_output.md")
        }