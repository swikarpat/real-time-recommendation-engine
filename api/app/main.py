from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import json
import requests  # For calling the inference service

app = FastAPI()

# Replace with your inference service URL
INFERENCE_SERVICE_URL = "http://your-inference-service:8000/predict"

# Connect to Redis for caching (Optional, but recommended)
cache = redis.Redis(host="your-redis-host", port=6379, db=0)  # Replace with your Redis host and port


class RecommendationRequest(BaseModel):
    user_id: int
    context: dict = {}  # Optional contextual information


class RecommendationResponse(BaseModel):
    recommendations: list


@app.post("/recommend", response_model=RecommendationResponse)
async def recommend(request: RecommendationRequest):
    user_id = request.user_id
    cache_key = f"recommendations:{user_id}"

    # Check if recommendations are cached (Optional)
    cached_recs = cache.get(cache_key)
    if cached_recs:
        return RecommendationResponse(recommendations=json.loads(cached_recs))

    # Get recommendations (replace with your recommendation logic)
    recommendations = await get_recommendations_for_user(user_id, request.context)

    # Cache the recommendations (Optional)
    cache.setex(cache_key, 300, json.dumps(recommendations))  # Cache for 5 minutes, adjust as needed

    return RecommendationResponse(recommendations=recommendations)


async def get_recommendations_for_user(user_id: int, context: dict):
    """
    Gets recommendations for a user by calling the inference service for multiple products.

    Args:
        user_id: The ID of the user.
        context:  Optional contextual information

    Returns:
        A list of product recommendations with scores.
    """
    # 1. Get a list of candidate product IDs (you'll need a strategy for this)
    # This could be based on:
    #   - Popularity
    #   - Category browsing history
    #   - Co-purchases/Co-views
    #   - etc.
    candidate_product_ids = get_candidate_products(user_id)

    # 2. Call the inference service for each product to get a score
    recommendations = []
    for product_id in candidate_product_ids:

        # Create request payload for inference service
        inference_request = {
            "user_id": user_id,
            "product_id": product_id,
            # ... (Add other features as needed by your model)
            "view_count": 0,  # Example: Replace with actual feature values
            "purchase_count": 0,
            "avg_time_spent_sec": 0.0,
            "category_view_count": 0,
            "category_purchase_count": 0,
            "user_id_index": 0,  # You might need to fetch these from a lookup table
            "product_id_index": 0,
            "category_index": 0,
        }

        try:
            response = requests.post(INFERENCE_SERVICE_URL, json=inference_request)
            response.raise_for_status()  # Raise an exception for bad status codes
            prediction = response.json()
            recommendations.append({"product_id": product_id, "score": prediction["score"]})
        except requests.exceptions.RequestException as e:
            print(f"Error calling inference service: {e}")
            # Handle the error (e.g., log it, skip the product, use a fallback)

    # 3. Sort recommendations by score (descending)
    recommendations.sort(key=lambda x: x["score"], reverse=True)

    return recommendations


def get_candidate_products(user_id: int):
    """
    Placeholder function to get a list of candidate product IDs for a user.

    Replace this with your actual logic to generate candidate products.
    """
    # Example: Return a list of popular products (you would likely query a database or use a more sophisticated method)
    return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Replace with actual product IDs