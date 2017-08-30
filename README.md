# WSQuiz
A quiz app used to demonstrate WebSockets and Django Channels in my talk [Django Unchanneled]().

The frontend was developed by my fellow friend [Douglas Gimli](https://github.com/douglasgimli). Thanks mate :heart:

## Installation and Usage
Basically, using Docker.

```bash
docker-compose up -d
docker-compose run web python manage.py collectstatic
```

To install some demo data, use:
```bash
docker-compose run web python manage.py loaddata questions.json
```

After, just access [your localhost](http://localhost) and start playing. It's more fun to play with your friends, you may use [ngrok](https://ngrok.com/) to expose your local network to the Internet!

If you want to create a superuser:
```bash
docker-compose run web python manage.py createsuperuser
```

We also have tests! To run them:
```bash
docker-compose run web python manage.py test
```
