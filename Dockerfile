FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the application files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 5000

# Run the application
CMD ["python", "backend/app.py"]
