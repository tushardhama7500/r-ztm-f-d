import time
import datetime
import random

def Stamp():
    event_number = random.randint(1000000000, 9999999999)
    now = datetime.datetime.now()
    event_time = now.strftime("%Y-%m-%d %H:%M:%S")
    return f"{event_time} [{event_number}]"