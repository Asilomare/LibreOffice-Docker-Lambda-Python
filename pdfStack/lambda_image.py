import subprocess
import sys
import os
import boto3
import json 

from lo_loader import load_libre_office

#Update with libreoffice exec path
OfficeExecutablePath = load_libre_office()

#def docToPdf(sourceFile, folder):
def docToPdf(event, context):

    s3 = boto3.client('s3')
    
    # Get trigger-event variables
    event_bucket_name = event['Records'][0]['s3']['bucket']['name']
    event_object_key = event['Records'][0]['s3']['object']['key']

    # Lambda functions can only write to tmp dir during runtime
    out_dir = "/tmp/"
    
    #debugging 
    print(f"bucket: {event_bucket_name}")
    print(f"event key : {event_object_key}")
    
    sourceFile = f"{out_dir}{event_object_key}"
    res = s3.download_file(event_bucket_name, 
                        event_object_key, 
                        sourceFile # local path
                    )
    
    #debugging 
    if os.path.exists(sourceFile):
        print(f"{sourceFile} exists!")
    else:
        print(f"{sourceFile} does not exist.")

    
    #debugging 
    print(f"office path: {OfficeExecutablePath}")
    print(f"sourcef: {sourceFile}")
    
    #Define CLI arguments for LibreOffice
    conv_cmd = f"{OfficeExecutablePath} --headless --norestore --invisible --nodefault --nofirststartwizard --nolockcheck --nologo --convert-to pdf:writer_pdf_Export --outdir /tmp {sourceFile}"
    
    # Have to run twice because of known issue with OfficeLibre
    # see https://github.com/shelfio/libreoffice-lambda-layer/issues/20
    response = subprocess.run(conv_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if response.returncode != 0:
        response = subprocess.run(conv_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if response.returncode != 0:
            raise ValueError("cannot convert this document to pdf")
    
    # Get the output file of OfficeLibre
    name, ext = os.path.splitext(sourceFile)
    newFilename = f"{name}.pdf"
    
    # Get name/path for outfile
    name, ext = os.path.splitext(event_object_key)
    oldFilename = event_object_key + '.pdf'
    oldFilename.replace(' ', '')
    
    
    print(f"name: {name}")
    print(f"old-name: {oldFilename}")
    print(f"new-name: {newFilename}")

    # upload file to same bucket
    s3.upload_file(newFilename,
                event_bucket_name,
                oldFilename
                )

    s3.close()
