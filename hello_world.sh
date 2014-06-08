#!/bin/bash

if [ -n "$1" ]; then
    NAME="$1"
else
    NAME="World"
fi

echo "Hello, $NAME!"

cat | base64
