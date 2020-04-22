#!/bin/sh

if ! grep "^caddy:" /etc/group &>/dev/null; then
	groupadd --system caddy
fi

if ! id caddy > /dev/null 2>&1; then
	useradd --system \
		--gid caddy \
		--create-home \
		--home-dir /var/lib/caddy \
		--shell /usr/sbin/nologin \
		--comment "Caddy web server" \
		caddy
fi
