FROM python:3.12-bullseye

WORKDIR /app

# Copy only Pipfile files first
COPY Pipfile Pipfile.lock ./

# Install pipenv and dependencies
RUN pip install pipenv && \
    PIPENV_VENV_IN_PROJECT=1 pipenv install --ignore-pipfile

# Copy the rest of the application
COPY . .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

EXPOSE 8000

# Use entrypoint script
CMD ["./entrypoint.sh"]