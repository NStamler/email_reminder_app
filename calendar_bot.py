# -*- coding: utf-8 -*-

import os
import datetime
from database import get_all_users
from emailer import send_email
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# === CONFIG ===
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "your_calendar_id@group.calendar.google.com")
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Authenticate with Google Calendar
def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def get_events_on_day(service, target_date):
    start = datetime.datetime.combine(target_date, datetime.time.min).isoformat() + 'Z'
    end = datetime.datetime.combine(target_date, datetime.time.max).isoformat() + 'Z'
    events_result = service.events().list(
        calendarId=CALENDAR_ID, timeMin=start, timeMax=end,
        singleEvents=True, orderBy='startTime').execute()
    return events_result.get('items', [])

def get_events_between(service, start_date, end_date):
    start = datetime.datetime.combine(start_date, datetime.time.min).isoformat() + 'Z'
    end = datetime.datetime.combine(end_date, datetime.time.max).isoformat() + 'Z'
    events_result = service.events().list(
        calendarId=CALENDAR_ID, timeMin=start, timeMax=end,
        singleEvents=True, orderBy='startTime').execute()
    return events_result.get('items', [])

def format_event_list(events):
    if not events:
        return "No events found."
    return '\n'.join(f"• {event.get('summary', '(No Title)')} at {event['start'].get('dateTime', event['start'].get('date'))}" for event in events)

def send_daily_reminders(service):
    today = datetime.date.today()
    for user in get_all_users():
        days_before = int(user[1])
        reminder_date = today + datetime.timedelta(days=days_before)
        scheduled_time = user[2]  # Not used for timing, but could be if queued

        events = get_events_on_day(service, reminder_date)
        if events:
            body = f"Hi!\n\nHere are your upcoming event(s) for {reminder_date}:\n\n"
            body += format_event_list(events)
            send_email(user[0], f"📅 Reminder for events on {reminder_date}", body)

def send_weekly_digests(service):
    today = datetime.date.today()
    weekday = today.strftime("%A")

    for user in get_all_users():
        if not user[3]:  # digest flag
            continue
        if user[4] != weekday:
            continue

        digest_time = user[5]  # Not used yet
        digest_range = user[6]
        if digest_range == "past":
            start_date = today - datetime.timedelta(days=7)
            end_date = today
        else:  # upcoming
            start_date = today
            end_date = today + datetime.timedelta(days=7)

        events = get_events_between(service, start_date, end_date)
        body = f"Hi!\n\nHere is your weekly digest ({digest_range} week):\n\n"
        body += format_event_list(events)
        send_email(user[0], f"🗓️ Weekly Digest – Events {digest_range}", body)

if __name__ == '__main__':
    service = get_calendar_service()
    send_daily_reminders(service)
    send_weekly_digests(service)
