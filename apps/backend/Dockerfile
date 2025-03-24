# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the application
CMD ["sh", "-c", "python -m app.scripts.init_db && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
