#!/bin/bash

# 1. Ensure pip is updated and installs Django
uv pip install -r requirements.txt --system --python 3.14

# 2. Run the collection process
python3 manage.py collectstatic --noinput --clear