#!/bin/bash

# 1. Ensure pip is updated and installs Django
pip install -r requirements.txt

# 2. Run the collection process
python3 manage.py collectstatic --noinput --clear