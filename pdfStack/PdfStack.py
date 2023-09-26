from aws_cdk import (
    App, 
    Stack,
    Duration,
    aws_s3 as s3,
    aws_iam as iam,
    aws_events as events,
    aws_lambda as _lambda,
    aws_s3_notifications as s3_notify,
    aws_apigateway as apigw,
)


class PdfStack(Stack):
    def __init__(self, app: App, id: str) -> None:
        super().__init__(app, id)

        output_bucket = s3.Bucket(self, 'pdfOutputBucket',
            lifecycle_rules=[
                s3.LifecycleRule(
                    expiration=Duration.days(15)
                )    
            ]
        )
        
        #lambda from docker image
        function = _lambda.DockerImageFunction(self, "pdfConvertFunction",
            code=_lambda.DockerImageCode.from_image_asset(
                directory="pdfStack/lambda_image/"),
            timeout=Duration.seconds(150),
            environment={ 
                 "HOME": '/tmp',
                 "FONTCONFIG_FILE": "/var/task/fonts/fonts.conf",
                 "BUCKET": output_bucket.bucket_name
            },
            memory_size=1024*4,  
        )
        
        # The function needs to download and upload files
        output_bucket.grant_read_write(function)
        
        api = apigw.LambdaRestApi(
            self, 'api',
            handler=function 
        )
        
        