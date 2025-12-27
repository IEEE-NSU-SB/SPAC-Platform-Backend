# pip install ics
from datetime import datetime
from zoneinfo import ZoneInfo
from ics import Calendar, Event

# Bangladesh timezone
tz = ZoneInfo("Asia/Dhaka")

# Event details
event_name = "SPAC 2025"
event_start = datetime(2025, 12, 29, 8, 30, tzinfo=tz)   # 8:30 AM Bangladesh time
event_end   = datetime(2025, 12, 29, 21, 0, tzinfo=tz)  # 9:00 PM Bangladesh time
event_location = "North South University, Dhaka, Bangladesh"
event_description = (
    "SPAC 2025 — The IEEE Student Professional Awareness Conference (SPAC) is a formal networking dinner connecting engineering and computer science students with esteemed industry professionals. IEEE NSU Student Branch aims to host the event with unparalleled grandeur and professionalism."
)
event_url = "https://spac25.ieeensusb.org/"
uid = "SPAC25@ieeensusb.org"

# Create calendar and event
cal = Calendar()
ev = Event(
    name=event_name,
    begin=event_start,
    end=event_end,
    location=event_location,
    description=event_description,
    url=event_url,
    uid=uid,
    created=datetime.now(tz),
    last_modified=datetime.now(tz)
)

cal.events.add(ev)

# Serialize and write ICS file
ics_text = cal.serialize()
ics_text_crlf = ics_text.replace("\r\n", "\n").replace("\n", "\r\n")

out_path = './event.ics'
with open(out_path, "w", encoding="utf-8", newline="") as f:
    f.write(ics_text_crlf)

print("ICS written to:", out_path)
