web: bash -c "if [ $DEV ]; then python manage.py runserver 0.0.0.0:$PORT; else gunicorn benchmarkci.wsgi --log-file - ; fi"
