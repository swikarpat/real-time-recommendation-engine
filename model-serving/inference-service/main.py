from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import tensorflow as tf
import redis
import json

app = FastAPI()

# Load the TensorFlow model
model = tf.keras.models.load_model("your-model-path")  # Replace with your model path

# Connect to Redis for caching
cache = redis.Redis(host="your-redis-host", port=6379, db=0)  # Replace with your Redis details


class PredictionRequest(BaseModel):
    user_id: int
    product_id: int
    # Add other features as needed
    view_count: int = 0
    purchase_count: int = 0
    avg_time_spent_sec: float = 0.0
    category_view_count: int = 0
    category_purchase_count: int = 0
    user_id_index: int = 0
    product_id_index: int = 0
    category_index: int = 0


class PredictionResponse(BaseModel):
    score: float


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    # Check if the prediction is cached
    cache_key = f"prediction:{request.user_id}:{request.product_id}"
    cached_score = cache.get(cache_key)
    if cached_score:
        return PredictionResponse(score=float(cached_score))

    # Prepare input features for the model
    try:
        features = {
            "user_id_index": [request.user_id_index],
            "product_id_index": [request.product_id_index],
            "view_count": [request.view_count],
            "purchase_count": [request.purchase_count],
            "avg_time_spent_sec": [request.avg_time_spent_sec],
            "category_view_count": [request.category_view_count],
            "category_purchase_count": [request.category_purchase_count],
            "category_index": [request.category_index]
        }

        # Get model prediction
        score = get_model_prediction(features)

        # Cache the prediction result
        cache.setex(cache_key, 3600, score)  # Cache for 1 hour

        return PredictionResponse(score=score)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during prediction: {str(e)}")

def get_model_prediction(features):
    # Perform model prediction
    predictions = model(features)
    # Assuming the model output is a probability
    score = predictions.numpy()[0][0]
    return score