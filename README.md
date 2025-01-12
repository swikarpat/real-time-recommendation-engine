# Real-Time Recommendation Engine

This data engineering project implements a real-time recommendation engine for an e-commerce platform.

# Runbook

This document provides guidelines for troubleshooting and maintaining the real-time recommendation engine.

## Troubleshooting

### Common Issues and Solutions

1.  **Problem:** Recommendations are not updating in real-time.

    *   **Possible Causes:**
        *   Issues with the Kafka consumers.
        *   Problems with the real-time processing application (Flink/Spark Streaming).
        *   Connectivity problems between components.

    *   **Troubleshooting Steps:**
        *   Check the logs of the Kafka consumers for any errors.
        *   Check the logs of the Flink/Spark Streaming application.
        *   Verify that Kafka brokers are running and accessible.
        *   Check network connectivity between components.
        *   Use monitoring dashboards (Grafana) to identify bottlenecks or errors.

2.  **Problem:** API is slow to respond.

    *   **Possible Causes:**
        *   High load on the API.
        *   Slow inference from the model serving layer.
        *   Inefficient database queries.
        *   Network latency.

    *   **Troubleshooting Steps:**
        *   Check the API server logs.
        *   Monitor API response times using Grafana dashboards.
        *   Check the load and performance of the model serving infrastructure.
        *   Optimize database queries if necessary.
        *   Use a caching layer (Redis) to reduce latency.

3.  **Problem:** Model accuracy is degrading.

    *   **Possible Causes:**
        *   Data drift (changes in user behavior or data distribution).
        *   Concept drift (changes in the relationship between features and the target variable).
        *   Issues with the model training pipeline.

    *   **Troubleshooting Steps:**
        *   Monitor model performance metrics (AUC, precision, recall) using dashboards.
        *   Retrain the model more frequently.
        *   Investigate data quality issues.
        *   Consider using more advanced models or features.

### Monitoring and Alerting

*   **Monitoring:** The system is monitored using Prometheus and Grafana. Dashboards are available to visualize key metrics.
*   **Alerting:** Alerts are configured for critical issues, such as:
    *   High error rates in the API or data pipelines.
    *   High latency in the API or model serving.
    *   Low resource utilization (CPU, memory) indicating potential bottlenecks.
    *   Significant drops in model accuracy.

### Maintenance

*   **Regular Tasks:**
    *   Monitor system performance and resource utilization.
    *   Review logs for errors and warnings.
    *   Update dependencies and patch software vulnerabilities.
    *   Retrain models periodically.
*   **Data Pipeline Maintenance:**
    *   Ensure data pipelines are running smoothly.
    *   Monitor data quality and address any issues.
*   **Model Maintenance:**
    *   Retrain models with fresh data.
    *   Evaluate model performance and consider improvements.
*   **Infrastructure Maintenance:**
    *   Monitor and manage cloud resources (e.g., S3, EMR, Redshift, SageMaker).
    *   Scale resources up or down as needed.

## Escalation Procedures

Refer to docs/data_dictionary.md

# Real-Time Recommendation Engine Data Dictionary

This document describes the data sources, schemas, and features used in the real-time recommendation engine.

## Data Sources

1.  **User Interactions:**
    *   **Source:** Kafka topic: `clickstream-events`, Kafka topic: `purchase-events`
    *   **Description:** Real-time stream of user interactions, including clicks, views, add-to-cart, and purchases.
    *   **Schema:**
        *   `user_id` (INT): Unique identifier for the user.
        *   `product_id` (INT): Unique identifier for the product.
        *   `event_type` (VARCHAR): Type of event (e.g., "view", "purchase", "click", "add_to_cart").
        *   `timestamp` (TIMESTAMP): Timestamp of the event.
        *   `session_id` (VARCHAR): Identifier for the user's session.
        *   `metadata` (JSON): Additional information about the event (e.g., page URL, referrer).

2.  **Product Catalog:**
    *   **Source:** CSV file (`product_catalog.csv`)
    *   **Description:** Information about the products in the catalog.
    *   **Schema:**
        *   `product_id` (INT): Unique identifier for the product.
        *   `product_name` (VARCHAR): Name of the product.
        *   `category` (VARCHAR): Category of the product.
        *   `price` (DECIMAL): Price of the product.
        *   `description` (TEXT): Description of the product.
        *   `attributes` (JSON): Additional attributes of the product (e.g., color, size).

3.  **Users (Optional):**
    *   **Source:** Database or CRM
    *   **Description:** Information about users (if available).
    *   **Schema:**
        *   `user_id` (INT): Unique identifier for the user.
        *   `user_name` (VARCHAR): Name of the user.
        *   `email` (VARCHAR): Email address of the user.
        *   `demographics` (JSON): Demographic information about the user (e.g., age, gender, location).

## Data Warehouse Tables

1.  **`user_interactions` Table:**
    *   Stores user interaction events.

2.  **`products` Table:**
    *   Stores product catalog information.

3.  **`users` Table (Optional):**
    *   Stores user information.

## Features

This section describes the features engineered from the raw data.

**User Features:**

*   `user_product_views`: Number of times a user has viewed each product.
*   `user_product_purchases`: Number of times a user has purchased each product.
*   `user_product_avg_time`: Average time spent by a user on each product page.
*   `user_category_views`: Number of times a user has viewed each product category.
*   `user_category_purchases`: Number of times a user has purchased each product category.
*   `user_last_interaction`: Recency of the user's last interaction.

**Other Features:**

*   Features derived from the `metadata` field in user interactions.
*   Features derived from the `attributes` field in the product catalog.
*   Features derived from the `demographics` field in the users table (if available).

## Feature Store (if applicable)

notebooks/data_exploration.ipynb

Python
import pandas as pd

#### Load data from S3 or your data warehouse
#### Example: Loading data from a CSV file in S3
```df = pd.read_csv("s3://your-bucket/path/to/your/data.csv")```

### Explore the data
```
print(df.head())
print(df.info())
print(df.describe())
```
# Perform data analysis and visualization
model-training/training-jobs/requirements.txt

tensorflow
horovod
pyspark
model-serving/inference-service/requirements.txt

fastapi
uvicorn
tensorflow
redis
pydantic
api/app/requirements.txt

fastapi
uvicorn
redis
pydantic
requests
orchestration/dags/requirements.txt

apache-airflow[amazon]
requirements.txt

# Data Ingestion
kafka-python
boto3

# Data Processing
pyspark==3.1.2 # Specify compatible version for your EMR cluster
pyflink==1.15.0

# Model Training
tensorflow==2.9.0
horovod==0.28.0

# Model Serving
fastapi==0.95.0
uvicorn==0.21.1
redis==4.5.4
pydantic==1.10.7

# API
requests==2.28.2

# Orchestration
apache-airflow[amazon]==2.5.0

# Testing
pytest==7.3.1
pytest-cov==4.0.0

# Other
pandas==1.5.3
scikit-learn==1.2.2
README.md

# Real-Time Recommendation Engine

This project implements a real-time recommendation engine for an e-commerce platform.

## Project Structure

<pre>
real-time-recommendation-engine/
├── data-ingestion/           # Code for ingesting data from various sources
├── data-storage/             # Scripts and configuration for data storage
├── data-processing/          # Code for batch and real-time data processing
├── model-training/           # Code for training recommendation models
├── model-serving/            # Code for deploying and serving models
├── api/                      # Code for the recommendation API
├── orchestration/            # Scripts and configuration for workflow orchestration
├── monitoring/               # Scripts and configuration for monitoring
├── infrastructure/           # Infrastructure as Code (IaC)
├── notebooks/                # Jupyter notebooks for experimentation
├── scripts/                  # Utility scripts
├── tests/                    # Unit and integration tests
├── docs/                     # Documentation
├── requirements.txt          # Python dependencies
└── README.md                 # Project overview
</pre>

## Getting Started

### Prerequisites
* AWS Account
* Python 3.9 or greater
* Docker
* Terraform
* Kubernetes (optional)
* ...

### Installation

## 1. Clone the repository:
```
git clone https://github.com/your-username/real-time-recommendation-engine.git
cd real-time-recommendation-engine
```
## Install dependencies:
```
pip install -r requirements.txt
```

### Setup
1. Configure AWS credentials:
2. Set up your AWS credentials as environment variables or in a credentials file.
### Create infrastructure:
1. Navigate to the infrastructure/aws/ directory.
2. Run terraform init to initialize Terraform.
3. Run terraform apply to create the necessary AWS resources.
### Deploy the API and Inference Service:
1. Follow the deployment instructions in api/deployment/README.md and model-serving/deployment-scripts/README.md (if applicable).

### Usage
1. Start the data ingestion process.
2. Run the Airflow DAGs for batch processing and model training.
3. Access the recommendation API to get recommendations.

### Running Tests
```pytest```

### Documentation

#### See the docs/ directory for more detailed documentation, including:
1. architecture.md: System architecture overview.
2. runbook.md: Troubleshooting and maintenance guide.
3. data_dictionary.md: Description of data sources and features.
