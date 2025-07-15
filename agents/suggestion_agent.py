# agents/suggestion_agent.py

from datetime import timedelta
from agents.negotiator import negotiate_meeting
from main_utils import find_common_slots, find_partial_slots

MIN_DURATION = timedelta(minutes=30)

def suggest_meeting_slot(agent1, agent2, duration=MIN_DURATION):
    print(f"\n🤖 Suggesting meeting slot for {agent1.get_name()} and {agent2.get_name()}...")

    # 1. Try full common slots
    free1 = agent1.get_free_slots()
    free2 = agent2.get_free_slots()
    common = find_common_slots(free1, free2, duration)

    if common:
        print("✅ Suggested Common Free Slot:")
        return common[0]

    # 2. Try negotiation
    print("⚠️ No direct slot found. Trying to negotiate...")
    if negotiate_meeting(agent1, agent2) or negotiate_meeting(agent2, agent1):
        free1 = agent1.get_free_slots()
        free2 = agent2.get_free_slots()
        common = find_common_slots(free1, free2, duration)
        if common:
            print("✅ Found slot after rescheduling:")
            return common[0]

    # 3. Fallback to partial
    print("❌ Still no full match. Checking partial overlaps...")
    partials = find_partial_slots(free1, free2, min_duration_minutes=15)
    if partials:
        print("💡 Suggested partial overlap:")
        return partials[0]

    # 4. Give up
    print("🚫 No available slot found.")
    return None
