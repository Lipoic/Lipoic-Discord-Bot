# Lipoic-Discord-Bot

the bot of Lipoic official discord server

# setup

```sh
pip install pipenv
pipenv install # or $ pipenv install --dev
pipenv shell
```

# run

## pipenv

```sh
python main.py
```

## docker

```sh
# build
pipenv lock -r > requirements.txt
docker build -t lipoic-bot . --no-cache
# run
docker run -d lipoic-bot
```
