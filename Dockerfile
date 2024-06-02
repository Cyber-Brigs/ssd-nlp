# Use the official Python image from the Docker Hub (Debian-based)
FROM python:3.9-buster

# Set environment variables to prevent Python from writing .pyc files and to buffer stdout and stderr
ENV PYTHONUNBUFFERED=1 
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory within the container
WORKDIR /usr/src/app 

# Copy requirements file
COPY requirements.txt .

# Install pip and build tools for compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpython3-dev \
    tzdata \
    libc-dev

# Upgrade pip 
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools wheel
RUN pip install cython


# Install all dependencies
RUN pip install --no-cache-dir -r requirements.txt 

# Download NLTK stopwords 
RUN python -m nltk.downloader stopwords

# Install SpaCy and model
RUN pip install --no-cache-dir "spacy[all]" \
    && python3 -m spacy download en_core_web_sm

RUN pip install --upgrade PyMuPDF  
  # && pip install --uninstall scipy==1.12.13


# Make the run script executable
COPY ./devops/scripts/run_app.sh ./devops/scripts/
RUN chmod +x ./devops/scripts/run_app.sh  

# Copy the rest of the project files 
COPY . .


# Expose port 8000
EXPOSE 8000

# Run the Django server
CMD ["./devops/scripts/run_app.sh"]
