import pandas as pd
import boto3
from io import StringIO

def upload_csv_to_s3(csv_file, bucket, s3_file):
    """Upload a CSV file to an S3 bucket."""
    s3 = boto3.client('s3')
    try:
        csv_buffer = StringIO()
        csv_file.to_csv(csv_buffer, index=False)
        s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket, Key=s3_file)
        print(f"CSV file uploaded to s3://{bucket}/{s3_file}")
    except Exception as e:
        print(f"Error uploading CSV file: {e}")

# Load the product catalog data from a CSV file
product_catalog_df = pd.read_csv("product_catalog.csv")

# Define your S3 bucket and file name
bucket_name = "your-s3-bucket-name"  # Replace with your S3 bucket name
s3_file_name = "product-catalog/product_catalog.csv"

# Upload the product catalog data to S3
upload_csv_to_s3(product_catalog_df, bucket_name, s3_file_name)