from kafka import KafkaConsumer
import json
import boto3
from botocore.exceptions import NoCredentialsError

def upload_to_s3(data, bucket, s3_file):
    """Upload data to an S3 bucket."""
    s3 = boto3.client('s3')
    try:
        s3.put_object(Body=data, Bucket=bucket, Key=s3_file)
        print(f"Data uploaded to s3://{bucket}/{s3_file}")
    except FileNotFoundError:
        print("The file was not found")
    except NoCredentialsError:
        print("Credentials not available")

consumer = KafkaConsumer(
    'clickstream-events',
    bootstrap_servers=['broker1:9092', 'broker2:9092'],  # Replace with your Kafka brokers
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='clicks-consumer-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

bucket_name = 'your-s3-bucket-name'  # Replace with your S3 bucket name

for message in consumer:
    event = message.value
    print(f"Received click event: {event}")

    # Upload the event data to S3
    s3_file_name = f'clickstream/event_{message.timestamp}.json'
    upload_to_s3(json.dumps(event), bucket_name, s3_file_name)