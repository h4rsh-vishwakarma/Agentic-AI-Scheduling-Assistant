import json
from agents.calendar_agent import CalendarAgent
from agents.negotiator import negotiate_meeting
from datetime import timedelta

# Minimum required duration for a valid common meeting
MIN_DURATION = timedelta(minutes=30)
def find_common_slots(slots1, slots2, min_duration=MIN_DURATION):
    """Find exact common slots between two agents with required duration."""
    common = []
    for start1, end1 in slots1:
        for start2, end2 in slots2:
            start = max(start1, start2)
            end = min(end1, end2)
            if start < end and (end - start) >= min_duration:
                common.append((start, end))
    return common

def find_partial_slots(slots1, slots2, min_duration_minutes=15):
    """Find partial overlaps that are at least min_duration_minutes long."""
    partials = []
    for start1, end1 in slots1:
        for start2, end2 in slots2:
            start = max(start1, start2)
            end = min(end1, end2)
            duration = (end - start).total_seconds() / 60
            if duration >= min_duration_minutes:
                partials.append((start, end))
    return partials
def format_slot(slot, tz):
    """Format datetime slot into HH:MM format in local time."""
    start_local = slot[0].astimezone(tz).strftime('%H:%M')
    end_local = slot[1].astimezone(tz).strftime('%H:%M')
    return f"{start_local} - {end_local}"