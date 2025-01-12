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

**Product Features:**

*   (You can add product-specific features here if needed)

**Other Features:**

*   Features derived from the `metadata` field in user interactions.
*   Features derived from the `attributes` field in the product catalog.
*   Features derived from the `demographics` field in the users table (if available).

## Feature Store (if applicable)

[Describe the features stored in the feature store, their data types, and how they are accessed]