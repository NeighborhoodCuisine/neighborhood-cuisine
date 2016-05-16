#! /bin/bash

# source: https://github.com/apidoc/apidoc

cd $(dirname $0)/..
apidoc -i ./ -e docs -o docs -f ".*\\.py"
