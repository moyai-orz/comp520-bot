set dotenv-load

default:
  just --list

fmt:
  poetry run black .

start-bot:
  poetry run python App/main.py

deploy:
  nohup just start-bot && disown > output.log 2>&1  &
