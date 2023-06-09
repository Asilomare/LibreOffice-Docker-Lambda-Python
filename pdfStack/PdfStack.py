from aws_cdk import (
    aws_lambda as _lambda,
    aws_events as events,
    aws_iam as iam,
    aws_s3 as s3,
    aws_s3_notifications as s3_notify,
    App, Stack, Duration
)

# Change this value 
_BUCKET_ = 'testbucket22245454123'

class PdfStack(Stack):
    def __init__(self, app: App, id: str) -> None:
        super().__init__(app, id)

        bucket = s3.Bucket.from_bucket_name(self, "internal_bucket_name", _BUCKET_)
        
        #lambda from docker image
        function = _lambda.DockerImageFunction(self, "pdfConverter",
            code=_lambda.DockerImageCode.from_image_asset(
                directory="pdfStack/lambda_image/"),
            timeout=Duration.seconds(150),
            environment={ 
                 "HOME": '/tmp',
                 "FONTCONFIG_FILE": "/var/task/fonts/fonts.conf"
            },
            memory_size=1000,  
        )
        
        # The function needs to download and upload files
        bucket.grant_read_write(function)
        
        notification = s3_notify.LambdaDestination(function)
        notification.bind(self, bucket)

        # Touch base about these specifics
        bucket.add_object_created_notification(
            notification, s3.NotificationKeyFilter(suffix='.doc')
           )
        bucket.add_object_created_notification(
           notification, s3.NotificationKeyFilter(suffix='.docx')
        )
        """
        TO ADD MORE SUFFIX TRIGGERS, ADD STATEMENT:
        bucket.add_object_created_notification(
           notification, s3.NotificationKeyFilter(suffix='SUFFIX_HERE')
        )
        """
