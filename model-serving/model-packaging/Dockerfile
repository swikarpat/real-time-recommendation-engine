# Use an appropriate base image (e.g., a Python image with TensorFlow)
FROM tensorflow/tensorflow:2.9.0-gpu

# Set working directory
WORKDIR /app

# Copy the inference service code
COPY inference-service /app/inference-service
COPY model-training/core-models/ /app/model-training/core-models

# Install dependencies
RUN pip install --no-cache-dir -r /app/inference-service/requirements.txt

# Expose the port the inference service will run on
EXPOSE 8000

# Command to run the inference service
CMD ["uvicorn", "inference-service.main:app", "--host", "0.0.0.0", "--port", "8000"]