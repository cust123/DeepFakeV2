# Use a slim Python base image
FROM python:3.10-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Explicitly copy the model file to ensure it's included in the image
COPY Google_Colab_my_deepfake_model_with_fine_tuning_04_April_part2.keras /app/

# Expose the port gunicorn will use
EXPOSE 5000

# Run the Flask app via gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
