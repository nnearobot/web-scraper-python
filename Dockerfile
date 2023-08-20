FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install required libraries
RUN pip install --no-cache-dir requests beautifulsoup4 lxml

# Make the script executable
RUN chmod +x main.py

# Create a volume for the archives
VOLUME /app/pages

# Command to run the script
ENTRYPOINT ["python3", "main.py"]
