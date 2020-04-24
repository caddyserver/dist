#!/bin/sh
set -e

if [ -d /run/systemd/system ] && [ "$1" = remove ]; then
	deb-systemd-invoke stop caddy >/dev/null || true
	deb-systemd-invoke stop caddy-api >/dev/null || true
fi