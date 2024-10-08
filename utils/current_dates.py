from datetime import datetime, timedelta

def current_date():
    return datetime.now().date()

def today_and_tomorrow():
    t = datetime.now()
    today = t.strftime('%d.%m')
    tom = t + timedelta(days=1)
    tomorrow = tom.strftime('%d.%m')
    return today, tomorrow


