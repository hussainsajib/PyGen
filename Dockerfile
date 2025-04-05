# Use a slim base image to reduce the image size
FROM python:3.9-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first, to enable caching
COPY requirements.txt .

# Install MoviePy and its dependencies
RUN apt-get update && apt-get upgrade -y \
    && pip install --upgrade pip \
    && apt-get install ffmpeg libsm6 libxext6  -y \
    && pip install --no-cache-dir -r requirements.txt
    
# Copy the rest of the application code
COPY . .

# Expose the port if needed (adjust if your application requires a specific port)
EXPOSE 8000

#RUN ["uvicorn", "app:app", "--reload"]