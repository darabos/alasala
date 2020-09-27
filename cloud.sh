#!/bin/bash -xue

yarn build
firebase deploy # Frontend to Firebase Hosting.
gcloud app deploy # Backend to App Engine.
