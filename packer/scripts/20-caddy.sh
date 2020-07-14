#!/bin/bash
set -eux;

echo "deb [trusted=yes] https://apt.fury.io/caddy/ /" | tee -a /etc/apt/sources.list.d/caddy-fury.list
apt update
apt install caddy

mkdir -p /var/www/html
chown -R caddy:caddy /var/www
