FROM python:3.12-bullseye

WORKDIR /app

# Copy only Pipfile files first
COPY Pipfile Pipfile.lock ./

# Install pipenv and dependencies
RUN pip install pipenv && \
    PIPENV_VENV_IN_PROJECT=1 pipenv install --ignore-pipfile

# Copy the rest of the application
COPY . .

EXPOSE 8000

# Use pipenv run with shell form to ensure proper environment
CMD pipenv run python manage.py runserver 0.0.0.0:8000