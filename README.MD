# What is this?

This is a parser with Django-based admin panel. Parser is set up to parse articles from habr.com, based on 'Habrs'
(topics). Each Habr's main page can be parsed automatically, to get articles, and then each article can be parsed
(automatically as well), to get:

- Articles header
- Articles text
- Author name
- Author link
- Publication date

# Main functions

1. Set up intervals in which each individual Habr will be parsed
2. Turn on/off each individual Habr
3. Force re-parsing for any specific Article (set checkbox "Спарсить" to do so)

# Launching

**IMPORTANT: TESTED ON WINDOWS ONLY!**

## Development mode

1. Load this repo using GIT
2. Create venv
3. Open command-prompt and navigate to root folder (habr_parser)
4. Run:

```console
pip install -r requirements.txt
```

5. To launch admin panel navigate to parser_console and run:

```console
python manage.py runserver
```

6. Use user_name and password 'super' or create your own user instead
7. To launch parser-app navigate to parser_app an run main.py

Admin-panel and parser-app can work independently

## Docker mode:

**WARNING: NOT TESTED PROPERLY!**

Execute:
```console
docker-compose up
```

Or to run in detached mode (no console output):
```console
docker-compose up -d
```