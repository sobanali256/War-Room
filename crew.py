from crewai import Crew, Process
from agents import WarRoomAgents
from tasks import WarRoomTasks

class WarRoomCrew:
    # CHANGE 1: __init__ now accepts user_role and counter_party
    def __init__(self, contract_text, user_role="The User", counter_party="The Counterparty"):
        self.contract_text = contract_text
        self.user_role = user_role
        self.counter_party = counter_party
        self.agents = WarRoomAgents()
        self.tasks = WarRoomTasks()

    def run(self):
        # CHANGE 2: Pass roles to Agents
        shark = self.agents.shark_agent(self.counter_party)
        shield = self.agents.shield_agent(self.user_role)
        mediator = self.agents.mediator_agent()

        # CHANGE 3: Pass roles to Tasks
        attack = self.tasks.attack_task(shark, self.contract_text, self.counter_party)
        
        defense = self.tasks.defense_task(
            shield, 
            self.contract_text, 
            context=[attack], 
            user_role=self.user_role
        )
        
        verdict = self.tasks.verdict_task(mediator, self.contract_text, context=[attack, defense])

        # Create Crew
        crew = Crew(
            agents=[shark, shield, mediator],
            tasks=[attack, defense, verdict],
            process=Process.sequential,
            verbose=True
        )

        return crew.kickoff()