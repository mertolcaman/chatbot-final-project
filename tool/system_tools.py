from datetime import datetime, timedelta
from langchain.tools import tool

system_tools=[]

from datetime import datetime, timedelta
from langchain.tools import tool

@tool
def get_current_datetime(input: str = "") -> dict:
    """
    Returns the current date/time, the day of the week, and the season.
    If input is 'tomorrow', returns tomorrow's date and day.
    Useful for timestamp logic like opening hours, checking current time/day, and seasonal checks.
    """
    now = datetime.now()

    if input.strip().lower() == "tomorrow":
        target = now + timedelta(days=1)
    else:
        target = now

    # Determine the season
    month = target.month
    day = target.day

    if (month == 12 and day >= 21) or (1 <= month <= 2) or (month == 3 and day < 20):
        season = "Winter"
    elif (month == 3 and day >= 20) or (4 <= month <= 5) or (month == 6 and day < 21):
        season = "Spring"
    elif (month == 6 and day >= 21) or (7 <= month <= 8) or (month == 9 and day < 22):
        season = "Summer"
    else:
        season = "Autumn"

    return {
        "iso": target.isoformat(),
        "day_of_week": target.strftime("%A"),  # e.g., Monday, Tuesday
        "season": season
    }


system_tools.append(get_current_datetime)
