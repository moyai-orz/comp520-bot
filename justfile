set dotenv-load

alias d := deploy
alias f := fmt
alias r := run

default:
  just --list

fmt:
  ruff check --select I --fix && ruff format

deploy branch='main' domain='173.255.231.30':
  ssh root@{{domain}} "mkdir -p deploy \
    && apt-get update --yes \
    && apt-get upgrade --yes \
    && apt-get install --yes git rsync"
  rsync -avz deploy/checkout root@{{domain}}:deploy/checkout
  ssh root@{{domain}} 'cd deploy && ./checkout {{branch}} {{domain}}'

run:
  poetry run python app/main.py
