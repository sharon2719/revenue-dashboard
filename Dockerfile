# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
# We'll set it to /app, and then copy the web_app content into it.
WORKDIR /app

# Copy the requirements file first to leverage Docker's layer caching
COPY requirements.txt .

# Install any needed Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of your web_app directory (where app.py now resides)
# into the /app directory inside the container.
COPY src/web_app/ .

# Set the Google Cloud Project ID as an environment variable.
# IMPORTANT: Replace 'your-google-cloud-project-id' with your actual GCP Project ID.
ENV GOOGLE_CLOUD_PROJECT=revenue-dashboard-demo

# Expose the port that your Flask application will listen on
EXPOSE 8080

# Define the command to run your Flask application when the container starts.
# Since app.py is now directly in /app (due to the COPY src/web_app/ .),
# this command remains the same.
CMD ["python", "app.py"]