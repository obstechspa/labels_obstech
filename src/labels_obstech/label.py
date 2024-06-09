#! /usr/bin/env python3

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_resource(path):

    from importlib import resources
    from pathlib import Path

    root = resources.files(__name__)
    return Path(root) / path

def make_label(
    hardware: str, 
    hwid:str, 
    filename: str = "{hardware}-{hwid}.lbx", 
    **kwargs
):
    """Generate labels for brother printers.

hardware:
    Type of hardware.  The generic label definition is stored under
    directory f'./{hardware}'.

hwid:
    Hardware identification code.

filename:
    Pattern for the label file name.  Can include any of the 
    arguments. Defaults to "{hardware}-{hwid}.lbx"
    
**kwargs:
    Parameters used in the generic label definition.

    """ 

    path = get_resource("data") / hardware
    if not path.exists():    
        path = Path(hardware)
        

    kwargs = dict(hardware=hardware, hwid=hwid, **kwargs)
    
    filename = filename.format(**kwargs)
    if '/' in filename:
        filename = filename.split('/')[-1]

    with ZipFile(filename, 'w', compression=ZIP_DEFLATED) as out:

        for file in path.glob('*'):

            name = file.name

            if name.endswith('xml'):
                with open(file, 'r') as in_:
                    contents = in_.read().format(**kwargs).encode()
            else:
                with open(file, 'rb') as in_:
                    contents = in_.read()

            out.writestr(name, contents)

    return filename

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

    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=sheet_id, range=range_name)
        .execute()
    )
    values = result.get("values", [])

    return values

def make_telescope_labels() -> None:

    sheet_id = '1rgqsUifjIKhl6pXm7DFsNiQsGiZKPDvuPoQ98Z6DuKc'
    range_id = "Telescope queues!A2:D"
    values = download_sheet(sheet_id, range_id)

    for hwid, owner, queue, roof in values:
        if hwid and owner and queue and roof:
            make_label(
                'telescope', 
                hwid=hwid, owner=owner, queue=queue, roof=roof  
            )

make_telescope_labels()
