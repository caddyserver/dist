#!/bin/sh
set -e

if [ -d /run/systemd/system ]; then
	systemctl --system daemon-reload >/dev/null || true
fi

if [ "$1" = "remove" ]; then
	if [ -x "/usr/bin/deb-systemd-helper" ]; then
		deb-systemd-helper mask caddy >/dev/null || true
		deb-systemd-helper mask caddy-api >/dev/null || true
	fi
fi

if [ "$1" = "purge" ]; then
	if [ -x "/usr/bin/deb-systemd-helper" ]; then
		deb-systemd-helper purge caddy >/dev/null || true
		deb-systemd-helper purge caddy-api >/dev/null || true
		deb-systemd-helper unmask caddy >/dev/null || true
		deb-systemd-helper unmask caddy-api >/dev/null || true
	fi
fi