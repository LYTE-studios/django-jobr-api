FROM python:3.12-bullseye

WORKDIR /app

# Copy only the Pipfile files first
COPY Pipfile Pipfile.lock ./

# Install dependencies in a separate layer
RUN pip install pipenv && \
    PIPENV_VENV_IN_PROJECT=1 pipenv sync

# Copy the rest of the application
COPY . .

EXPOSE 8000

# Use shell form to ensure proper environment activation
CMD pipenv run gunicorn -b 0.0.0.0:8000 jobr_api_backend.wsgi:application