#!/bin/bash -xue

export GOOGLE_CLOUD_PROJECT='alasala'
export OAUTHLIB_INSECURE_TRANSPORT=1
FLASK_APP=backend/main.py FLASK_ENV=development python -m flask run
