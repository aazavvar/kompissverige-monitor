import requests
from bs4 import BeautifulSoup
import json
import smtplib
import os
from email.mime.text import MIMEText

URL = "https://www.kompissverige.se/aktiviteter"

def get_events():
    response = requests.get(URL)
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
    sender = os.environ["EMAIL_USER"]
    password = os.environ["EMAIL_PASS"]
    receiver = os.environ["EMAIL_USER"]

    body = ""
    for event in new_events:
        body += f"{event['title']}\n{event['link']}\n\n"

    msg = MIMEText(body)
    msg["Subject"] = "New Event Added!"
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)


def main():
    current_events = get_events()
    old_events = load_old_events()

    new_events = [e for e in current_events if e not in old_events]

    if new_events:
        send_email(new_events)
        save_events(current_events)
    else:
        print("No new events.")


if __name__ == "__main__":
    main()
