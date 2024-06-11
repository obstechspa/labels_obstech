#! /usr/bin/env python3

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from pathlib import Path

def get_resource(path: str) -> Path:

    from importlib import resources
    from pathlib import Path

    root = resources.files(__name__)
    return Path(root) / path


def download_sheet(
    sheet_id: str, 
    range_name: str,    
    token_file: Path = Path('~/.config/labels_obstech/token.json'),
    credentials_file: Path = Path('~/.config/labels_obstech/credentials.json')
):

    # log in
    
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

    token_file = token_file.expanduser()
    credentials_file = credentials_file.expanduser()

    print(token_file)
    print(credentials_file)

    creds = None
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
             creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_file), SCOPES
            )
            creds = flow.run_local_server(port=0)
            with open(token_file, "w") as token:
                token.write(creds.to_json())

    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API

    sheets = service.spreadsheets()
    sheet = sheets.values().get(
        spreadsheetId=sheet_id, 
        range=range_name,
    )
    result = sheet.execute()
    values = result.get("values", [])

    return values

