FROM python:3.12-bullseye

WORKDIR /app

# Copy only the Pipfile files first
COPY Pipfile Pipfile.lock ./

# Install dependencies in a separate layer
RUN pip install pipenv && pipenv sync

# Copy the rest of the application
COPY . .

EXPOSE 8000

# Command to run the Python script
CMD ["pipenv", "run", "gunicorn", "-b", "0.0.0.0:8000", "jobr_api_backend.wsgi:application"]