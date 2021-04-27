#!/bin/sh -e

RESULT=$(curl "http://$1:$2/api/isodd/1337/")

echo "$RESULT" | grep "isodd"
echo "$RESULT" | grep "true"
echo "$RESULT" | grep "ad"

