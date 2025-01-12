from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.s3_to_redshift import S3ToRedshiftOperator
from airflow.providers.amazon.aws.operators.emr_create_job_flow import EmrCreateJobFlowOperator
from airflow.providers.amazon.aws.operators.emr_add_steps import EmrAddStepsOperator
from airflow.providers.amazon.aws.sensors.emr_step import EmrStepSensor
from airflow.providers.amazon.aws.operators.emr_terminate_job_flow import EmrTerminateJobFlowOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

# Define default arguments
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
        dag_id='recommendation_pipeline',
        default_args=default_args,
        schedule_interval='@daily',  # Set your desired schedule
        catchup=False,
        tags=['recommendation', 'pipeline'],
) as dag:
    # Task 1: Ingest data from S3 to Redshift (example)
    load_data_to_redshift = S3ToRedshiftOperator(
        task_id='load_data_to_redshift',
        schema="your_redshift_schema",  # Replace with your Redshift schema
        table="user_interactions",      # Replace with your Redshift table
        s3_bucket="your-s3-bucket",      # Replace with your S3 bucket
        s3_key="data-lake/raw/user-interactions/",  # Replace with your S3 key
        redshift_conn_id="redshift_default",  # Replace with your Redshift connection ID
        aws_conn_id="aws_default",            # Replace with your AWS connection ID
        copy_options=['FORMAT AS PARQUET'],
    )

    # Task 2: Create an EMR cluster
    create_emr_cluster = EmrCreateJobFlowOperator(
        task_id="create_emr_cluster",
        job_flow_overrides={
            "Name": "RecommendationEngineEMRCluster",
            "ReleaseLabel": "emr-6.3.0",  # Specify the EMR release version
            "Applications": [{"Name": "Spark"}, {"Name": "Hadoop"}, {"Name": "Hive"}, {"Name": "Horovod"}],  # Add required applications
            "Instances": {
                "InstanceGroups": [
                    {
                        "Name": "Master node",
                        "Market": "ON_DEMAND",
                        "InstanceRole": "MASTER",
                        "InstanceType": "m5.xlarge",  # Specify instance type
                        "InstanceCount": 1,
                    },
                    {
                        "Name": "Core nodes",
                        "Market": "ON_DEMAND",
                        "InstanceRole": "CORE",
                        "InstanceType": "m5.xlarge",  # Specify instance type
                        "InstanceCount": 2,  # Specify the number of core nodes
                    },
                ],
                "KeepJobFlowAliveWhenNoSteps": False,
                "TerminationProtected": False,
            },
            "VisibleToAllUsers": True,
            "ServiceRole": "EMR_DefaultRole",  # Ensure this role exists with proper permissions
            "JobFlowRole": "EMR_EC2_DefaultRole",  # Ensure this role exists with proper permissions
            # Add other necessary configurations
        },
        aws_conn_id="aws_default",  # Replace with your AWS connection ID
        region_name="your-aws-region",  # Replace with your AWS region
    )

    # Task 3: Define Spark step for batch feature engineering
    feature_engineering_step = [
        {
            "Name": "Batch Feature Engineering",
            "ActionOnFailure": "CONTINUE",
            "HadoopJarStep": {
                "Jar": "command-runner.jar",
                "Args": [
                    "spark-submit",
                    "--deploy-mode",
                    "cluster",
                    "--master",
                    "yarn",
                    "--num-executors",
                    "2",
                    "--executor-cores",
                    "2",
                    "s3://your-s3-bucket/data-processing/batch-processing/feature-engineering/batch_features.py",  # Path to your Spark application
                ],
            },
        }
    ]

    # Task 4: Add Spark step to EMR cluster
    add