# Use an official Python image as base
FROM python:3.10.11

# Set the working directory
WORKDIR /app

# Copy the requirements file. Copying it first allows Docker to cache the layer if requirements don't change
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose any required ports
EXPOSE 8501

# Define the command to run your application
CMD ["streamlit", "run", "main.py"]