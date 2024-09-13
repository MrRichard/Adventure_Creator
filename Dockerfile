# Use a small Python 3 base image
FROM python:3.12.6-slim

# Set working directory
WORKDIR /app

# Copy all content into the /app directory
COPY . .

RUN apt-get update && apt-get install -y python3-pip python3-venv

# Create a virtual environment in /app
RUN python -m venv .venv

# Install the dependencies from requirements.txt
RUN /app/.venv/bin/pip3 install -r requirements.txt

# Make run.sh executable
RUN chmod +x run.sh

# Specify the command that runs when the container starts
ENTRYPOINT ["/bin/bash", "run.sh"]