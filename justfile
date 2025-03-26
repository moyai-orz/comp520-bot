set dotenv-load

alias c := check
alias d := deploy
alias f := fmt
alias r := run

default:
  just --list

check:
  uv run ruff check --select I --fix && uv run mypy src

fmt:
  uv run ruff format

deploy branch='main' domain='173.255.231.30':
  ssh root@{{domain}} "mkdir -p deploy \
    && apt-get update --yes \
    && apt-get upgrade --yes \
    && apt-get install --yes git rsync"
  rsync -avz deploy/checkout root@{{domain}}:deploy/checkout
  ssh root@{{domain}} 'cd deploy && ./checkout {{branch}} {{domain}}'

run:
  uv run bot
