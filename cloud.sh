#!/bin/bash -xue

yarn build
#firebase deploy # Frontend to Firebase Hosting.
gcloud app deploy --project=alasala # Backend to App Engine.
