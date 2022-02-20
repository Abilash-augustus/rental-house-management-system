release: python manage.py migrate
web: gunicorn config.wsgi:application --log-file - --log-level debug
python3 manage.py collectstatic --noinput
