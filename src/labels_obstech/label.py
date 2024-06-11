#! /usr/bin/env python3

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from .utils import download_sheet, get_resource

def make_label(
    hardware: str, 
    hwid:str, 
    filename: str = "{hardware}-{hwid}.lbx", 
    **kwargs
) -> Path:

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
    lbx_file = Path(filename)

    with ZipFile(lbx_file, 'w', compression=ZIP_DEFLATED) as out:

        for file in path.glob('*'):

            name = file.name

            if name.endswith('xml'):
                with open(file, 'r') as in_:
                    contents = in_.read().format(**kwargs).encode()
            else:
                with open(file, 'rb') as in_:
                    contents = in_.read()

            out.writestr(name, contents)

    return lbx_file

def make_telescope_labels() -> None:

    sheet_id = '1rgqsUifjIKhl6pXm7DFsNiQsGiZKPDvuPoQ98Z6DuKc'
    range_id = "Telescope queues!A3:D"
    values = download_sheet(sheet_id, range_id)

    lbx_files = []

    for hwid, owner, queue, roof in values:
        if hwid and owner and queue and roof:
            lbx_file = make_label(
                'telescope', 
                hwid=hwid, owner=owner, queue=queue, roof=roof 
            )
            print(f"Making label file {lbx_file} for HWID={hwid}")
            lbx_files.append(lbx_file)
