FROM python:3.12-bullseye

WORKDIR /app

# Copy only the Pipfile files first
COPY Pipfile Pipfile.lock ./

# Install dependencies in a separate layer and create virtualenv in project directory
ENV PIPENV_VENV_IN_PROJECT=1
RUN pip install pipenv && \
    pipenv sync

# Copy the rest of the application
COPY . .

EXPOSE 8000

# Use the full path to gunicorn in the virtualenv
CMD . /app/.venv/bin/activate && \
    /app/.venv/bin/gunicorn -b 0.0.0.0:8000 jobr_api_backend.wsgi:application