import json
import pytz
from datetime import datetime

class CalendarAgent:
    def __init__(self, name, calendar_file=None, data=None):
        self.name = name
        if data:
            self.data = data
        else:
            self.data = self.load_calendar(calendar_file)

        self.timezone = pytz.timezone(self.data.get("timezone", "UTC"))

    def load_calendar(self, file_path):
        with open(file_path, 'r') as f:
            return json.load(f)

    def parse_time(self, day, time_str):
        local = self.timezone
        naive = datetime.strptime(f"{day} {time_str}", "%A %H:%M")
        return local.localize(naive).astimezone(pytz.utc)  # convert to UTC

    def get_free_slots(self):
        work_start = self.parse_time("Monday", self.data["working_hours"]["start"])
        work_end = self.parse_time("Monday", self.data["working_hours"]["end"])

        meetings = sorted(self.data["meetings"], key=lambda m: m["start"])
        busy_slots = [(self.parse_time(m["day"], m["start"]), self.parse_time(m["day"], m["end"])) for m in meetings]

        free_slots = []
        prev_end = work_start
        for start, end in busy_slots:
            if start > prev_end:
                free_slots.append((prev_end, start))
            prev_end = max(prev_end, end)

        if prev_end < work_end:
            free_slots.append((prev_end, work_end))

        return free_slots

    def get_reschedulable_meetings(self):
        return [m for m in self.data["meetings"] if m.get("reschedulable")]

    def try_reschedule(self, meeting):
        original_slot = (self.parse_time(meeting["day"], meeting["start"]),
                         self.parse_time(meeting["day"], meeting["end"]))
        duration = original_slot[1] - original_slot[0]

        temp_meetings = [m for m in self.data["meetings"] if m != meeting]
        temp_data = dict(self.data)
        temp_data["meetings"] = temp_meetings

        temp_agent = CalendarAgent(self.name + "_temp", data=temp_data)

        free_slots = temp_agent.get_free_slots()

        for start, end in free_slots:
            if end - start >= duration:
                meeting["start"] = start.astimezone(self.timezone).strftime("%H:%M")
                meeting["end"] = (start + duration).astimezone(self.timezone).strftime("%H:%M")
                return True
        return False

    def print_free_slots(self):
        print(f"\n📅 {self.name}'s Free Slots (Local Time - {self.timezone.zone}):")
        for slot in self.get_free_slots():
            local_start = slot[0].astimezone(self.timezone)
            local_end = slot[1].astimezone(self.timezone)
            print(" -", local_start.strftime("%H:%M"), "-", local_end.strftime("%H:%M"))

    def print_meetings(self):
        print(f"\n🗓️ {self.name}'s Meetings (Local Time - {self.timezone.zone}):")
        for m in self.data["meetings"]:
            print(f" - {m['day']} {m['start']} to {m['end']} | {m['title']} | Reschedulable: {m.get('reschedulable', False)}")

    def get_data(self):
        return self.data

    def get_name(self):
        return self.name

    def cli_interface(self):
        while True:
            print(f"\n🤖 Calendar Agent - {self.name}")
            print("1. View Meetings")
            print("2. View Free Slots")
            print("3. View Reschedulable Meetings")
            print("0. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                self.print_meetings()
            elif choice == "2":
                self.print_free_slots()
            elif choice == "3":
                print(f"\n🔄 Reschedulable Meetings for {self.name}:")
                for m in self.get_reschedulable_meetings():
                    print(f" - {m['day']} {m['start']} to {m['end']} | {m['title']}")
            elif choice == "0":
                break
            else:
                print("Invalid choice. Try again.")
    def get_meetings(self):
        """Return list of meetings."""
        return self.data.get("meetings", [])
