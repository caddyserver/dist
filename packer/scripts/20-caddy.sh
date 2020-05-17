#!/bin/bash
set -eux;

groupadd --system caddy
useradd --system \
    --gid caddy \
    --create-home \
    --home-dir /var/lib/caddy \
    --shell /usr/sbin/nologin \
    --comment "Caddy web server" \
    caddy

if getent group www-data >/dev/null; then
    usermod -aG www-data caddy
fi

chown -R caddy:caddy /var/lib/caddy

VERSION_SLUG=${CADDY_VERSION//v/}
wget -qO /tmp/caddy.tar.gz https://github.com/caddyserver/caddy/releases/download/"${CADDY_VERSION}"/caddy_"${VERSION_SLUG}"_linux_amd64.tar.gz
tar -xzf /tmp/caddy.tar.gz -C /usr/bin caddy
chmod +x /usr/bin/caddy
setcap cap_net_bind_service=+ep /usr/bin/caddy

mkdir /usr/share/caddy/
chmod 755 /usr/share/caddy/

mkdir -p /var/www/html
chown -R caddy:caddy /var/www

mkdir /etc/caddy
