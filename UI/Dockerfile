# Use the official Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# The build context is the project root, so we use a relative path from there.
COPY ./UI/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the shared module from the project root
COPY ./shared ./shared

# Copy the interactive client script
COPY ./UI/interactive_client.py .

# Define the command to run the script when the container starts
CMD ["python", "interactive_client.py"]