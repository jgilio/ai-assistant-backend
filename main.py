from fastapi import FastAPI
from pydantic import BaseModel
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64
from email.mime.text import MIMEText
import os

app = FastAPI()

# These environment variables will be set later in Render
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar"
]

def get_credentials():
    return Credentials(
        None,
        refresh_token=GOOGLE_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=SCOPES
    )

class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str

@app.post("/send-email")
def send_email(request: EmailRequest):
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    message = MIMEText(request.body)
    message["to"] = request.to
    message["subject"] = request.subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()

    return {"status": "Email sent successfully"}

class EventRequest(BaseModel):
    summary: str
    start: str
    end: str

@app.post("/create-event")
def create_event(request: EventRequest):
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    def ensure_timezone(dt: str):
    if "Z" not in dt and "+" not in dt:
        return dt + "Z"
    return dt

event = {
    "summary": request.summary,
    "start": {"dateTime": ensure_timezone(request.start)},
    "end": {"dateTime": ensure_timezone(request.end)},
}


    service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    return {"status": "Event created successfully"}
