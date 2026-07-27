#!/bin/bash

uv venv .venv --python 3.14
uv pip install -r requirements.txt

uv run manage.py collectstatic --noinput --clear