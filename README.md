# Lipoic-Discord-Bot

the bot of Lipoic official discord server

Please view `config.yml.example` and create a `config.yml` file.

## setup

```sh
pip install pipenv
pipenv install # or $ pipenv install --dev
pipenv shell
```

## run

### pipenv

```sh
python main.py
```

### docker

```sh
# build
pipenv lock -r > requirements.txt
docker build -t lipoic-bot . --no-cache
# run
docker run -e DISCORD_TOKEN={your token} -d lipoic-bot
```
