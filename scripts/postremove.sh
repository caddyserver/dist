#!/bin/sh
set -e

if [ -d /run/systemd/system ]; then
	systemctl --system daemon-reload >/dev/null || true
fi

if [ "$1" = "remove" ]; then
	if [ -x "/usr/bin/deb-systemd-helper" ]; then
		deb-systemd-helper mask caddy.service >/dev/null || true
		deb-systemd-helper mask caddy-api.service >/dev/null || true
	fi
fi

if [ "$1" = "purge" ]; then
	if [ -x "/usr/bin/deb-systemd-helper" ]; then
		deb-systemd-helper purge caddy.service >/dev/null || true
		deb-systemd-helper purge caddy-api.service >/dev/null || true
		deb-systemd-helper unmask caddy.service >/dev/null || true
		deb-systemd-helper unmask caddy-api.service >/dev/null || true
	fi
fi