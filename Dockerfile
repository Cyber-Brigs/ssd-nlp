# Use the official Python image from the Docker Hub
FROM python:3.9.10-alpine3.15

# Set environment variables to prevent Python from writing .pyc files and to buffer stdout and stderr
ENV PYTHONUNBUFFERED=TRUE

COPY requirements.txt .

# Install the dependencies
RUN mkdir -p /usr/src/app \    
    && pip install -r requirements.txt \
    && pip uninstall spacy pydantic pymupdf -y \
    && pip install pip install pymupdf \
    && pip install spacy[all] \
    && python3 -m spacy download en_core_web_sm
# Copy the current directory contents into the container at /code/
COPY . /usr/src/app

# Expose port 8000 to the outside world
EXPOSE 8000

# Run the Django server
CMD ["./devops/scripts/run_app.sh"]
