#!/bin/bash
set -e
cd "$(dirname "$0")"
if [ ! -d .venv ]; then python3 -m venv .venv; fi
source .venv/bin/activate
python -m pip install -r requirements.txt
if [ ! -f .env ]; then cp .env.example .env; fi
python manage.py migrate
python manage.py seed_demo
echo 'Abre http://127.0.0.1:8001/ en tu navegador. Ctrl+C detiene el servidor.'
python manage.py runserver 127.0.0.1:8001
