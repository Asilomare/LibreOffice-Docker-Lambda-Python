import sys
import os
import time
import json 
import boto3
import base64
import requests
import subprocess
from os import environ
from lo_loader import load_libre_office

s3 = boto3.client('s3')
bucket = environ['BUCKET']

#Update with libreoffice exec path
OfficeExecutablePath = load_libre_office()

#def docToPdf(input_file_path, folder):
def docToPdf(event, context):

    link = json.loads(event['body'])
    
    response = requests.get(link)
    
    file_name = str(time.time())
    file_extension = '.docx'
    
    out_dir = "/tmp/"
    input_file_path = f"{out_dir}{file_name}{file_extension}"
    
    # Write the decoded content to a local file
    with open(input_file_path, 'wb') as f:
        f.write(response.content)
    
    #Define CLI arguments for LibreOffice
    conv_cmd = f"{OfficeExecutablePath} --headless --norestore --invisible --nodefault --nofirststartwizard --nolockcheck --nologo --convert-to pdf:writer_pdf_Export --outdir /tmp {input_file_path}"
    
    # Have to run twice because of known issue with OfficeLibre
    # see https://github.com/shelfio/libreoffice-lambda-layer/issues/20
    response = subprocess.run(conv_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if response.returncode != 0:
        response = subprocess.run(conv_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if response.returncode != 0:
            raise ValueError("cannot convert this document to pdf")
    
    # Get the output file of OfficeLibre
    converted_object_key = f"pdf/{file_name}.pdf"

    s3.upload_file(input_file_path, bucket, f"docx/{file_name}{file_extension}")
    s3.upload_file(f"{out_dir}{file_name}.pdf", bucket, converted_object_key)
    
    # Generate presigned Urls
    converted_file_link = s3.generate_presigned_url('get_object',
        Params={
            'Bucket': bucket,
            'Key': converted_object_key
        },
        ExpiresIn=3600
    )
    
    input_file_link = s3.generate_presigned_url('get_object',
        Params={
            'Bucket': bucket,
            'Key': f"docx/{file_name}{file_extension}"
        },
        ExpiresIn=3600
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'input_file_link': input_file_link,
            'converted_file_link': converted_file_link
        })
    }
