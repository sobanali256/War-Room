from crewai import Crew, Process
from agents import WarRoomAgents
from tasks import WarRoomTasks
import os

class WarRoomCrew:
    def __init__(self, contract_text, user_role="The User", counter_party="The Counterparty"):
        self.contract_text = contract_text
        self.user_role = user_role
        self.counter_party = counter_party
        self.agents = WarRoomAgents()
        self.tasks = WarRoomTasks()

    def run(self):
        # 1. Init Agents
        shark = self.agents.shark_agent(self.counter_party)
        shield = self.agents.shield_agent(self.user_role)
        mediator = self.agents.mediator_agent()

        # 2. Init Tasks
        attack = self.tasks.attack_task(shark, self.contract_text, self.counter_party)
        defense = self.tasks.defense_task(shield, self.contract_text, [attack], self.user_role)
        verdict = self.tasks.verdict_task(mediator, self.contract_text, [attack, defense])

        # 3. Run Crew
        crew = Crew(
            agents=[shark, shield, mediator],
            tasks=[attack, defense, verdict],
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
                print(f"Memory read failed: {e}")

            # Priority 2: Read the File
            try:
                if os.path.exists(filename):
                    with open(filename, "r", encoding='utf-8') as f:
                        return clean_garbage(f.read())
            except Exception as e:
                print(f"File read failed: {e}")

            return "⚠️ Simulation Error: Output not generated. Please check terminal logs."

        # 5. Garbage Cleaner (Removes the 'description=' text if it appears)
        def clean_garbage(text):
            text = str(text)
            if text.strip().startswith("description=") or "description='" in text:
                return "⚠️ Data Cleaning Error: The agent returned metadata instead of text. Check terminal for raw output."
            return text

        # Return using INDEX (0=Shark, 1=Shield, 2=Mediator)
        return {
            "shark_report": get_output(0, "shark_output.md"),
            "shield_report": get_output(1, "shield_output.md"),
            "final_verdict": get_output(2, "verdict_output.md")
        }