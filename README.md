# Lipoic-Discord-Bot

the bot of Lipoic official discord server

## configs

### token

1. use command

```sh
python -m lipoic -t <<Your discord bot token>>
```

2. use `.env` or `env`
create `.env` file follow the format `.env.example`

### config

Please follow the format of `config.yml` set in `config.yml`.
( please run once )

## setup

```sh
pip install pipenv
pipenv install # or $ pipenv install --dev
pipenv shell
```

## run

### pipenv

```sh
python -m lipoic
```

### docker

```sh
# build
pipenv lock -r > requirements.txt
docker build -t lipoic-bot . --no-cache
# run
docker run -e DISCORD_TOKEN={your token} -d lipoic-bot
```
