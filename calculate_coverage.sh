cd jobr_api_backend

pipenv sync

pipenv run coverage erase

pipenv run coverage run --source='.' manage.py test

pipenv run coverage html
