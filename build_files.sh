#!/bin/bash

uv venv .venv --python 3.14
uv pip install -r requirements.txt

# 2. Run the collection process
python3 manage.py collectstatic --noinput --clear