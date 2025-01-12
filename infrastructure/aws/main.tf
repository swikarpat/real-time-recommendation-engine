# Configure the AWS Provider
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0" # Use a specific version
    }
  }
}

provider "aws" {
  region = "your-aws-region"  # Replace with your desired AWS region
}

# Create an S3 bucket for the data lake
resource "aws_s3_bucket" "data_lake" {
  bucket = "your-data-lake-bucket-name"  # Replace with a unique bucket name
  acl    = "private"
  # Add other configurations like versioning, encryption, etc. as needed
}

# Create an EMR cluster (simplified example)
resource "aws_emr_cluster" "recommendation_cluster" {
  name          = "RecommendationEngineCluster"
  release_label = "emr-6.3.0" # Specify EMR release
  applications = ["Spark", "Hadoop", "Hive", "Horovod"]
  service_role = "EMR_DefaultRole" # Make sure this role exists
  job_flow_role = "EMR_EC2_DefaultRole" # Make sure this role exists
  master_instance_group {
    instance_type = "m5.xlarge"
  }
  core_instance_group {
    instance_type = "m5.xlarge"
    instance_count = 2
  }
  # Add other configurations, security groups, etc. as needed
}

# ... (Add other resources like Redshift cluster, IAM roles, etc.)