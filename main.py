import json
from datetime import timedelta, datetime, date
from agents.calendar_agent import CalendarAgent
from agents.negotiator import negotiate_meeting
from agents.suggestion_agent import suggest_meeting_slot 
from agents.llm_agent import get_llm_response  # ✅ LLM
from main_utils import find_common_slots, find_partial_slots, format_slot

    
# Minimum required duration for a valid common meeting
MIN_DURATION = timedelta(minutes=30)


def build_calendar_summary(agent):
    summary = f"\n🗓️ {agent.get_name()}'s Meetings (Local Time - {agent.timezone}):\n"
    for m in agent.get_meetings():
        try:
            start = datetime.fromisoformat(m["start"]).astimezone(agent.timezone)
            end = datetime.fromisoformat(m["end"]).astimezone(agent.timezone)
        except ValueError:
            # fallback: build datetime assuming today’s date
            today = date.today().isoformat()
            start = datetime.fromisoformat(f"{today}T{m['start']}:00").astimezone(agent.timezone)
            end = datetime.fromisoformat(f"{today}T{m['end']}:00").astimezone(agent.timezone)

        title = m.get("title", "No Title")
        reschedulable = m.get("reschedulable", False)
        summary += f" - {start.strftime('%A %H:%M')} to {end.strftime('%H:%M')} | {title} | Reschedulable: {reschedulable}\n"
    return summary


# -------- Utility Functions --------
def save_updated_calendar(agent, filename):
    """Save the updated calendar data for agent into a JSON file."""
    with open(filename, 'w') as f:
        json.dump(agent.get_data(), f, indent=4)
    print(f"💾 Saved updated calendar for {agent.get_name()} → {filename}")

# -------- Main Flow --------

# Step 1: Create agents
alice = CalendarAgent("Alice", "data/alice.json")
bob = CalendarAgent("Bob", "data/bob.json")

# Step 2: Get free slots for both agents
alice_free = alice.get_free_slots()
bob_free = bob.get_free_slots()

# Step 3: Print each agent's free slots
alice.print_free_slots()
bob.print_free_slots()

# Step 4: Find and print common meeting slots
common_slots = find_common_slots(alice_free, bob_free, MIN_DURATION)
print("\n✅ Common Available Slots (in local times):")
for slot in common_slots:
    print(f" 🟢 {alice.get_name()}: {format_slot(slot, alice.timezone)}")
    print(f" 🟢 {bob.get_name()}:   {format_slot(slot, bob.timezone)}")

# Step 5: If no common slot, attempt negotiation
if not common_slots:
    print("\n⚠️ No perfect common slots found. Trying reschedule...")

    negotiation_success = negotiate_meeting(alice, bob)
    if not negotiation_success:
        negotiation_success = negotiate_meeting(bob, alice)

    if negotiation_success:
        alice_free = alice.get_free_slots()
        bob_free = bob.get_free_slots()
        common_slots = find_common_slots(alice_free, bob_free, MIN_DURATION)

        print("\n✅ Updated Common Available Slots (after negotiation):")
        for slot in common_slots:
            print(f" 🟢 {alice.get_name()}: {format_slot(slot, alice.timezone)}")
            print(f" 🟢 {bob.get_name()}:   {format_slot(slot, bob.timezone)}")

        save_updated_calendar(alice, "data/alice_updated.json")
        save_updated_calendar(bob, "data/bob_updated.json")
    else:
        print("\n❌ No rescheduling could resolve the conflict.")

        # Step 6: Suggest partial overlaps
        partial_slots = find_partial_slots(alice_free, bob_free, min_duration_minutes=15)
        if partial_slots:
            print("\n💡 Suggested Partial Overlaps (Short Sync Options):")
            for slot in partial_slots:
                print(f" 🔹 {alice.get_name()}: {format_slot(slot, alice.timezone)}")
                print(f" 🔹 {bob.get_name()}:   {format_slot(slot, bob.timezone)}")
        else:
            print("\n❌ Even no partial overlaps found.")

# Step 7: Final AI-based Suggestion
suggested_slot = suggest_meeting_slot(alice, bob)
if suggested_slot:
    print(f"\n📌 Suggested Meeting Time (UTC): {suggested_slot[0]} - {suggested_slot[1]}")
    print(f"⏰ {alice.get_name()} Local: {suggested_slot[0].astimezone(alice.timezone).strftime('%H:%M')} - {suggested_slot[1].astimezone(alice.timezone).strftime('%H:%M')}")
    print(f"⏰ {bob.get_name()} Local: {suggested_slot[0].astimezone(bob.timezone).strftime('%H:%M')} - {suggested_slot[1].astimezone(bob.timezone).strftime('%H:%M')}")

    # Step 8: Use LLM to generate a natural language message
    alice_summary = build_calendar_summary(alice)
    bob_summary = build_calendar_summary(bob)

    prompt = f"""
    You are a smart scheduling assistant. Your task is to suggest a polite, friendly message that Alice and Bob can send each other to finalize a meeting.

    Here are their current schedules:

    {alice_summary}

    {bob_summary}

    They have finally found a common available slot:
    🕒 Meeting Time: {suggested_slot[0]} to {suggested_slot[1]} UTC

    Generate a polite suggestion message (like an email or message).
    """

    print("\n🧠 LLM Suggestion (Natural Language Summary):")
    print(get_llm_response(prompt))

  
else:
    print("\n⚠️ No feasible time could be suggested.")
