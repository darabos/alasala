#!/bin/bash -xue

yarn build
mkdir -p /tmp/alasaladep
pushd /tmp/alasaladep
rm -rf *
git clone git@github.com:darabos/alasala.git
popd
cp -r build /tmp/alasaladep/alasala/
pushd /tmp/alasaladep
zip -r alasala.zip alasala

echo "Zip file availabe at /tmp/alasaladep/alasala.zip"
