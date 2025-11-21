from crew import WarRoomCrew

# 1. Simulate a LEASE Scenario (Not a Freelance one!)
# This proves the agents are not hardcoded anymore.
fake_contract = """
The Tenant shall pay a security deposit of $5,000. 
The Landlord retains the right to enter the premises at any time 
without notice for inspections. 
If the Tenant breaks the lease, the Landlord may seize all personal property.
"""

print("--- STARTING MANUAL TEST: TENANT VS LANDLORD ---")

# 2. Initialize the Crew with explicit roles
# If your code is correct, the Shark should defend the Landlord.
war_room = WarRoomCrew(
    contract_text=fake_contract,
    user_role="The Tenant",
    counter_party="The Landlord"
)

# 3. Run it
result = war_room.run()

print("\n\n########################")
print("## FINAL RESULT ##")
print("########################\n")
print(result)