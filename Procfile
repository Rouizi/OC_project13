web: gunicorn car_rental.wsgi --log-file - --log-level debug
worker: python manage.py celery worker --loglevel=info
celery_beat: python manage.py celery beat --loglevel=info
