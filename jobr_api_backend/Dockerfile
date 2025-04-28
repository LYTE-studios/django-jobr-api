FROM python:3.12-bullseye

WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "jobr_api_backend.wsgi:application"]