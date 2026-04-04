#!/usr/bin/env bash

BASE="$(dirname "$(realpath "$0")")"

echo "Creazione cartelle in: $BASE"

mkdir -p \
  "$BASE/Tools" \
  "$BASE/Inbox" \
  "$BASE/Archive" \
  "$BASE/Temp" \
  "$BASE/Log" \
  "$BASE/Users/Admin" \
  "$BASE/Users/User"

echo
echo "Fatto."
