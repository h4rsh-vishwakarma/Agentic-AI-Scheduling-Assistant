from datetime import timedelta

def negotiate_meeting(requester, responder, min_duration=timedelta(minutes=30)):
    print(f"\n🤝 Negotiation: {requester.get_name()} ↔ {responder.get_name()}")

    # Get all potential new common slots after responder reschedules one meeting
    for meeting in responder.get_reschedulable_meetings():
        print(f"📩 {requester.get_name()} → {responder.get_name()}:")
        print(f"   ⏳ Can we reschedule your '{meeting['title']}' at {meeting['start']} to free up time?")

        # Try to reschedule that meeting
        if responder.try_reschedule(meeting):
            print(f"✅ {responder.get_name()} agreed to move '{meeting['title']}' to {meeting['start']} - {meeting['end']}")
            
            # Check if now there is a valid common slot
            requester_free = requester.get_free_slots()
            responder_free = responder.get_free_slots()

            for start1, end1 in requester_free:
                for start2, end2 in responder_free:
                    overlap_start = max(start1, start2)
                    overlap_end = min(end1, end2)
                    if overlap_start < overlap_end and (overlap_end - overlap_start) >= min_duration:
                        print(f"🎉 Common slot unlocked: {overlap_start.strftime('%H:%M')} - {overlap_end.strftime('%H:%M')}")
                        return True  # Negotiation success

    print(f"🙅‍♂️ {responder.get_name()} couldn't reschedule anything useful.")
    return False
