release: python manage.py migrate
web: daphne wsquiz.asgi:channel_layer --port $PORT --bind 0.0.0.0
worker: python manage.py runworker
