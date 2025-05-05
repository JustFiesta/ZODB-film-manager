FROM python:3.12-slim

WORKDIR /app

# Copy application files
COPY requirements.txt . 
COPY app/ ./app/ 
COPY web/ ./web/ 
COPY run.py .

# Install dependencies 
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables 
ENV FLASK_APP=web 
ENV FLASK_ENV=production 
ENV FLASK_RUN_HOST=0.0.0.0 
ENV PYTHONUNBUFFERED=1 
ENV LOG_LEVEL=DEBUG

# Expose port 
EXPOSE 5000

# Run the application 
CMD ["python", "run.py"]