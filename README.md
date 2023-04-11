# PDF Conversion AWS CDK Stack

This is a CDK Stack that creates an S3 bucket and an AWS Lambda function to convert Microsoft Word documents (.doc and .docx) to PDFs using LibreOffice.
This CDK Stack creates a lambda function from a locally built docker image, gives the function read & write permissions to a specified bucket, and sets up a trigger from the bucket, upon object create with certain suffixes (.doc, .docx) the lambda is invoked. 
The docker image installs the dependancies, scripts, and zipped OfficeLibre into the image. 
Once the stack is deployed and an event triggers the lambda, the script decompresses and caches LibreOffice for optimal runtime.
Once LibreOffice is loaded, the script downloads the event file -> converts to pdf -> uploads new file to event s3

## Installation

You also need to modify the `_BUCKET_` variable in `PdfStack.py` with your own bucket name.

## Methods

### Zipped LibreOffice

The maximum allowable packaging of code to upload to Lambdas from any source is 250MB, LibreOffice unzipped is closer to 500MB, this is a solved problem in Node.js but not in python.
However using the contents of a layer intended for node.js (see above download link), I did not have to optimize the application as someone else did this already. 
This package coupled with brotli decompression made plenty of room for the libre office in the lambda.

### Reasoning for fonts.conf

LibreOffice requires font files to be present on the system in order to render documents properly. By default, AWS Lambda does not have all the required fonts installed. To fix this issue, we provide a `fonts.conf` file that tells LibreOffice where to look for the fonts. This file is mounted inside the Lambda function's Docker container at the path `/var/task/fonts/fonts.conf`.

## Usage

The following are easiest from the cloud9 CLI, as AWSCLI and CDK are pre-installed and conifigured.
To deploy this stack, clone this repository, navigate to the root directory of your CDK app and run the following commands:

```sh
cdk bootstrap
pip install -r requirements.txt
cdk deploy
```

## CleanUp

Once deployed, to cleanup this stack run the following command

```sh
cdk destroy
```


