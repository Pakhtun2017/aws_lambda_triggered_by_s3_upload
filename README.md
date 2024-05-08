AWS Lambda function responds to events triggered by new object uploads to an S3 bucket. It processes these events to potentially read the content of the uploaded objects, logs specific information about these objects. It sends notifications via Amazon SNS.

Setup:
1) Create 2 S3 buckets, one for uploading the Zip file below and one that triggers events by new object upload, to which Lambda function responds
    aws s3 mb s3://<unique-name> --region <region-name>

2) Zip the Python file:
    zip -r s3_lambda_triggered.zip s3_lambda_triggered.py

3) Upload the Zip file to an S3 bucket. 
    aws s3 cp s3_lambda_triggered.zip s3://<bucket-for-zip>

4) Create an Execution Role for Lambda function
    aws iam create-role --role-name <role-name> \
        --assume-role-policy-document file://trust-policy.json

    aws iam attach-role-policy --role-name <role-name> \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

5) Attach the provided, lambda-s3-policy.json to Lambda Execution Role. This policy lists buckets and objects and gets content of object. 
    aws iam create-policy --policy-name LambdaS3AccessPolicy \
        --policy-document file://lambda-s3-policy.json

    aws iam attach-role-policy --role-name LambdaS3SNSExecutionRole \
        --policy-arn <arn of LambdaS3AccessPolicy>

    aws iam list-attached-role-policies \
        --role-name LambdaS3SNSExecutionRole

6) Create SNS topic and subscription 
    aws sns create-topic --name <name-of-topic>

    aws sns subscribe --topic-arn <topic-arn> \
        --protocol Email \
        --notification-endpoint <email-address>

7) Attach the provided, sns-publish-policy.json to the Lambda Execution Role. This policy allows Lambda function to send message to the topic. 
    aws iam create-policy  --policy-name <SNS Policy Name> \
        --policy-document file://sns-publish-policy.json

    aws iam attach-role-policy --role-name LambdaS3SNSExecutionRole \
        --policy-arn <arn of SNS Policy>

8) Create the Lambda function. This Lambda function will be triggered every time an object is uploaded to a designated S3 bucket. Lambda will send a message to SNS topic. Email subscribed to the topic receives an emaild

    aws lambda create-function \
        --function-name lambda_triggered_by_s3 \
        --runtime python3.9 \
        --handler lambda_triggered_by_s3.lambda_handler \
        --role <arn of Lambda Execution Role>
        --environment "Variables={S3_BUCKET_NAME=pashtun2,SNS_TOPIC_ARN=<arn of SNS topic>}" \
        --zip-file fileb://lambda_triggered_by_s3.zip

9) Add permissions to allow the S3 bucket to invoke your Lambda 
    aws lambda add-permission --function-name lambda_triggered_by_s3 \
        --statement-id s3-invoke-event-1 --action ""lambda:InvokeFunction"" \
        --principal s3.amazonaws.com --source-arn <arn of s3 bucket that invokes Lambda function with each upload>

10) Configure S3 bucket notification to invoke Lambda function
    aws s3api put-bucket-notification-configuration --bucket <arn of s3 bucket> \
        --notification-configuration '{
            "LambdaFunctionConfigurations": [
                {
                    "Id": "1",
                    "LambdaFunctionArn": "<Lambda function arn>",
                    "Events": ["s3:ObjectCreated:*"]
                }
            ]
        }'

