# Use an official Python runtime as the base image
FROM python:3.9

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the current directory into the container at /app
COPY . /app

# Expose the port that Django runs on
EXPOSE 8000

# Run the command to start the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
