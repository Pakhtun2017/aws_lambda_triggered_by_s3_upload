import os
import boto3
import json
import logging

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

# AWS clients
sns_client = boto3.client('sns')
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        if S3_BUCKET_NAME and bucket != S3_BUCKET_NAME:
            logger.warning(f"Event from unexpected bucket: {bucket}")
            continue

        try:
            response = s3_client.get_object(Bucket=bucket, Key=key)
            content_type = response['ContentType']

            text_content_types = ['text/plain', 'application/json', 'application/xml', 'text/csv']
            if content_type in text_content_types:
                try:
                    content = response['Body'].read().decode('utf-8')
                    logger.info(f"Object {key} created in bucket {bucket}. Content: {content}")
                except UnicodeDecodeError as e:
                    logger.error(f"Failed to decode content of {key} as UTF-8: {str(e)}")
                    content = "Content could not be decoded."
            else:
                content = "Non-text file, content not shown."
                logger.info(f"Object {key} created in bucket {bucket}. Content type: {content_type}")


            # Publish a notification if SNS topic ARN is set
            if SNS_TOPIC_ARN:
                message = {
                    'message': f"Object {key} created in bucket {bucket}."
                }
                sns_client.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Subject='S3 Object Created',
                    Message=json.dumps(message)
                )
        except Exception as e:
            logger.error(f"An error occurred while processing {key}: {str(e)}")
            continue

    return {
        'statusCode': 200,
        'body': json.dumps('Notification sent for processed files!')
    }
