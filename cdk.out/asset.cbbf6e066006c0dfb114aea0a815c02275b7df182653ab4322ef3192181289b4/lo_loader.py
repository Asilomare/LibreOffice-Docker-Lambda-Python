import os
from io import BytesIO
import tarfile

import brotli

LIBRE_OFFICE_INSTALL_DIR = '/tmp/instdir'

"""
Loads LibreOffice binary from a cached directory or extracts it from a compressed tar stream.

Returns:
    str: The file path to the LibreOffice binary.

Raises:
    FileNotFoundError: If the compressed tar stream or extracted LibreOffice directory does not exist.

Example:
    >>> soffice_path = load_libre_office()
    We have a cached copy of LibreOffice, skipping extraction
    >>> print(soffice_path)
    /tmp/instdir/program/soffice.bin
    

"""

def load_libre_office():
    if os.path.exists(LIBRE_OFFICE_INSTALL_DIR) and os.path.isdir(LIBRE_OFFICE_INSTALL_DIR):
        print('We have a cached copy of LibreOffice, skipping extraction')
    else:
        print('No cached copy of LibreOffice exists, extracting tar stream from Brotli file...')
        buffer = BytesIO()
        with open('/opt/lo.tar.br', 'rb') as brotli_file:
            decompressor = brotli.Decompressor()
            while True:
                chunk = brotli_file.read(1024)
                buffer.write(decompressor.decompress(chunk))
                if len(chunk) < 1024:
                    break
            buffer.seek(0)

        print('Extracting tar stream to /tmp for caching...')
        with tarfile.open(fileobj=buffer) as tar:
            tar.extractall('/tmp')
        print('Done caching LibreOffice!')
        
    return '{}/program/soffice.bin'.format(LIBRE_OFFICE_INSTALL_DIR)
