import os
import json
from datetime import timedelta 

from agents.calendar_agent import CalendarAgent
from agents.negotiator import negotiate_meeting
from agents.suggestion_agent import suggest_meeting_slot
from main_utils import find_common_slots, find_partial_slots, format_slot
from web.pdf_generator import generate_calendar_pdf

def save_updated_calendar(agent, filename_json):
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(BASE_DIR)
    SAVE_JSON_DIR = os.path.join(PROJECT_ROOT, "web", "static", "updated")
    SAVE_PDF_DIR = os.path.join(PROJECT_ROOT, "web", "static", "pdfs")

    os.makedirs(SAVE_JSON_DIR, exist_ok=True)
    os.makedirs(SAVE_PDF_DIR, exist_ok=True)

    # Save JSON
    json_path = os.path.join(SAVE_JSON_DIR, filename_json)
    with open(json_path, 'w') as f:
        json.dump(agent.get_data(), f, indent=4)
    print(f"💾 JSON saved at: {json_path}")

    # Generate PDF
    filename_pdf = filename_json.replace(".json", ".pdf")
    pdf_path = os.path.join(SAVE_PDF_DIR, filename_pdf)
    generate_calendar_pdf(agent.get_name(), agent.get_data(), pdf_path)

def run_scheduling(alice_file, bob_file, min_duration=30):
    """
    Core scheduling logic for Alice and Bob.
    Args:
        alice_file, bob_file: absolute paths to JSON files
        min_duration: minimum meeting duration in minutes
    """
    alice = CalendarAgent("Alice", alice_file)
    bob = CalendarAgent("Bob", bob_file)

    alice_free = alice.get_free_slots()
    bob_free = bob.get_free_slots()

    alice.print_free_slots()
    bob.print_free_slots()

    common_slots = find_common_slots(alice_free, bob_free, timedelta(minutes=min_duration))
    print("\n✅ Common Available Slots (in local times):")
    for slot in common_slots:
        print(f" 🟢 {alice.get_name()}: {format_slot(slot, alice.timezone)}")
        print(f" 🟢 {bob.get_name()}:   {format_slot(slot, bob.timezone)}")

    if not common_slots:
        print("\n⚠️ No perfect common slots found. Trying reschedule...")

        if not negotiate_meeting(alice, bob):
            negotiate_meeting(bob, alice)

        alice_free = alice.get_free_slots()
        bob_free = bob.get_free_slots()
        common_slots = find_common_slots(alice_free, bob_free, timedelta(minutes=min_duration))

        if common_slots:
            print("\n✅ Updated Common Available Slots (after negotiation):")
            for slot in common_slots:
                print(f" 🟢 {alice.get_name()}: {format_slot(slot, alice.timezone)}")
                print(f" 🟢 {bob.get_name()}:   {format_slot(slot, bob.timezone)}")

            save_updated_calendar(alice, "alice_updated.json")
            save_updated_calendar(bob, "bob_updated.json")
        else:
            print("\n❌ No rescheduling could resolve the conflict.")
            partial = find_partial_slots(alice_free, bob_free, min_duration_minutes=15)
            if partial:
                print("\n💡 Suggested Partial Overlaps:")
                for slot in partial:
                    print(f" 🔹 {alice.get_name()}: {format_slot(slot, alice.timezone)}")
                    print(f" 🔹 {bob.get_name()}:   {format_slot(slot, bob.timezone)}")
            else:
                print("\n❌ Even no partial overlaps found.")

    print("\n🤖 Suggesting meeting slot for Alice and Bob...")
    suggestion = suggest_meeting_slot(alice, bob)
    if suggestion:
        print(f"\n📌 Suggested Meeting Time (UTC): {suggestion[0]} - {suggestion[1]}")
        print(f"⏰ {alice.get_name()} Local: {suggestion[0].astimezone(alice.timezone).strftime('%H:%M')} - {suggestion[1].astimezone(alice.timezone).strftime('%H:%M')}")
        print(f"⏰ {bob.get_name()} Local: {suggestion[0].astimezone(bob.timezone).strftime('%H:%M')} - {suggestion[1].astimezone(bob.timezone).strftime('%H:%M')}")
    else:
        print("\n⚠️ No feasible time could be suggested.")
    # Final check: confirm PDFs were generated
    ROOT = os.path.dirname(os.path.abspath(__file__))
    alice_pdf_path = os.path.join(ROOT, "web", "static", "pdfs", "alice_updated.pdf")
    bob_pdf_path   = os.path.join(ROOT, "web", "static", "pdfs", "bob_updated.pdf")

    print(f"\n✅ PDF Exists Check:")
    print(f"  - Alice → {os.path.exists(alice_pdf_path)} | Path: {alice_pdf_path}")
    print(f"  - Bob   → {os.path.exists(bob_pdf_path)} | Path: {bob_pdf_path}")
    # ✅ Always save final updated calendars and generate PDFs
    print("\n📝 Saving updated calendars...")
    save_updated_calendar(alice, "alice_updated.json")
    save_updated_calendar(bob, "bob_updated.json")
