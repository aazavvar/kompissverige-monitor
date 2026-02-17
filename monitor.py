import requests
from bs4 import BeautifulSoup
import json
import smtplib
import os
from email.mime.text import MIMEText

URL = "https://www.kompissverige.se/aktiviteter"

def get_events():
    try:
        response = requests.get(URL, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching page: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    events = []
    for item in soup.find_all("a"):
        link = item.get("href")
        text = item.get_text(strip=True)
        if link and "/aktiviteter/" in link and text:
            full_link = "https://www.kompissverige.se" + link
            events.append({"title": text, "link": full_link})
    return events

def load_old_events():
    try:
        with open("events.json", "r") as f:
            return json.load(f)
    except:
        return []

def save_events(events):
    with open("events.json", "w") as f:
        json.dump(events, f)

def send_email(new_events):
    if not new_events:
        return
    sender = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")
    receiver = sender

    body = "\n\n".join([f"{e['title']}\n{e['link']}" for e in new_events])
    msg = MIMEText(body)
    msg["Subject"] = f"{len(new_events)} New Event(s) Added!"
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(sender, password)
            server.send_message(msg)
        print(f"Sent email for {len(new_events)} new events.")
    except Exception as e:
        print(f"Error sending email: {e}")

def main():
    current_events = get_events()
    if not current_events:
        print("No events fetched. Exiting.")
        return

    old_events = load_old_events()
    new_events = [e for e in current_events if e not in old_events]

    if new_events:
        send_email(new_events)
        save_events(current_events)
    else:
        print("No new events.")

if __name__ == "__main__":
    main()
