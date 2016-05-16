#! /bin/bash

# source: https://github.com/Zambonilli/node-apidoc-markdown

cd $(dirname $0)/..
./scripts/build-apidoc.sh
apidoc-markdown -p docs -o docs/github-apidoc.md
