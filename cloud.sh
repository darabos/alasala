#!/bin/bash -xue

yarn build
#firebase deploy # Frontend to Firebase Hosting.

# Backend to App Engine.
gcloud app deploy --project=alasala --quiet 
