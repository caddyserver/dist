#!/bin/bash

groupadd --system caddy
useradd --system \
    --gid caddy \
    --create-home \
    --home-dir /var/lib/caddy \
    --shell /usr/sbin/nologin \
    --comment "Caddy web server" \
    caddy

chown -R caddy:caddy /var/lib/caddy

VERSION_SLUG=$(echo "$CADDY_VERSION" | sed 's/-/_/g' | sed 's/\.[0-9]*\.[0-9]*//g' | sed 's/v//g')
wget -qO /usr/bin/caddy https://github.com/caddyserver/caddy/releases/download/"${CADDY_VERSION}"/caddy"${VERSION_SLUG}"_linux_amd64
chmod +x /usr/bin/caddy
setcap cap_net_bind_service=+ep /usr/bin/caddy

mkdir /usr/share/caddy/
chmod 755 /usr/share/caddy/

mkdir -p /var/www/html
chown -R caddy:caddy /var/www

mkdir /etc/caddy
