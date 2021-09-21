#!/bin/bash

if [ -n "$1" ]; then
    NAME="$1"
else
    NAME="World"
fi

echo "Hello, $NAME!"

if [[ -e README.md ]]; then 
  head -6 README.md | tail -5
fi

cat
