FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# The build context is the project root, so we use a relative path from there.
COPY ./RAG-Components/PII-filter/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the shared module from the project root
COPY ./shared ./shared

# Copy the PII filtering script
COPY ./RAG-Components/PII-filter/PII-filtering.py .

# Define the command to run the script when the container starts
CMD ["python", "PII-filtering.py"]