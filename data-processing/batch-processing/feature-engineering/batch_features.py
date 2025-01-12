from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder.appName("BatchFeatureEngineering").getOrCreate()

# Load data from S3
user_interactions = spark.read.parquet("s3a://your-bucket/data-lake/raw/user-interactions/")
products = spark.read.parquet("s3a://your-bucket/data-lake/raw/products/")

# Feature Engineering

# 1. Number of times a user has viewed each product
user_product_views = user_interactions.filter(col("event_type") == "view") \
    .groupBy("user_id", "product_id") \
    .count() \
    .withColumnRenamed("count", "view_count")

# 2. Number of times a user has purchased each product
user_product_purchases = user_interactions.filter(col("event_type") == "purchase") \
    .groupBy("user_id", "product_id") \
    .count() \
    .withColumnRenamed("count", "purchase_count")

# 3. Average time spent by a user on a product page (assuming you have start and end times)
# This is a simplification - you would likely calculate time differences between events
user_product_avg_time = user_interactions.filter(col("event_type").isin(["view_start", "view_end"])) \
    .groupBy("user_id", "product_id", "session_id") \
    .agg(max("timestamp").alias("end_time"), min("timestamp").alias("start_time")) \
    .withColumn("time_spent", unix_timestamp(col("end_time")) - unix_timestamp(col("start_time"))) \
    .groupBy("user_id", "product_id") \
    .agg(avg("time_spent").alias("avg_time_spent_sec"))

# 4. Number of times a user has viewed each product category
product_categories = products.select("product_id", "category")
user_category_views = user_interactions.filter(col("event_type") == "view") \
    .join(product_categories, "product_id") \
    .groupBy("user_id", "category") \
    .count() \
    .withColumnRenamed("count", "category_view_count")

# 5. Number of times a user has purchased each product category
user_category_purchases = user_interactions.filter(col("event_type") == "purchase") \
    .join(product_categories, "product_id") \
    .groupBy("user_id", "category") \
    .count() \
    .withColumnRenamed("count", "category_purchase_count")

# 6. Recency of user's last interaction
user_last_interaction = user_interactions.groupBy("user_id") \
    .agg(max("timestamp").alias("last_interaction_time"))

# Join features (you might want to do this in multiple steps for clarity)
user_features = user_product_views.join(user_product_purchases, ["user_id", "product_id"], "full") \
    .join(user_product_avg_time, ["user_id", "product_id"], "full") \
    .join(user_category_views, ["user_id"], "full") \
    .join(user_category_purchases, ["user_id"], "full") \
    .join(user_last_interaction, ["user_id"], "full")


# Write features to the data warehouse
user_features.write.mode("overwrite").parquet("s3a://your-bucket/data-warehouse/features/user_features/")

spark.stop()