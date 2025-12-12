#!/usr/bin/env bash
set -e

clear
clear

docker compose down

docker compose up -d --build