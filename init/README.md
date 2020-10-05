Official service files for systemd
==================================

This folder contains the officially-maintained systemd files that should be used as a basis for your own deployments.

**⚠️ Always review your service file before using it! Change anything that you need to customize.**

## Instructions

See our website for [installation instructions](https://caddyserver.com/docs/install).


## Prerequisites

Running Caddy as a systemd service requires the following:


Group named `caddy`:

```bash
$ groupadd --system caddy
```

User named `caddy` with a writeable home folder:

```bash
$ useradd --system \
    --gid caddy \
    --create-home \
    --home-dir /var/lib/caddy \
    --shell /usr/sbin/nologin \
    --comment "Caddy web server" \
    caddy
```


## Choosing a service file

- **`caddy.service`** - Use this one if you configure Caddy with a file (for example, the Caddyfile, or a .json file).
- **`caddy-api.service`** - Use this one if you configure Caddy solely through its API.

The two files are identical except for the ExecStart and ExecReload commands.

The usual place to save the service file is: `/etc/systemd/system/caddy.service`

## Important

Caddy receives all configuration through its [admin API](https://caddyserver.com/docs/api), even when the [command line interface (CLI)](https://caddyserver.com/docs/command-line) is used, which simply wraps up the API calls for you.

Most users will use either config files and the CLI [mutually exclusively](https://caddyserver.com/docs/getting-started#api-vs-config-files) with the API because it is simpler to have only one source of truth. However, you may wish to provide Caddy an initial "bootstrapping" configuration with a config file, and use the API thereafter.

**⚠️ If you provide an initial config file with the `--config` flag and then update the config using the API, you risk losing your changes if the service is restarted unless you have the `--resume` flag in your ExecStart command.**

Without the `--resume` flag, the `--config` flag will overwrite any last-known configuration.

However, it is totally safe and normal to use both the `--config` and `--resume` options together if you need to use both a config file and the API. Just be aware that if you update your config file and want to apply those changes, _stopping and starting the server is the wrong way to do this_. Restarting the service is orthogonal to config changes; this is a unique safety feature that guarantees durability and prevents data loss. If the config file has the latest changes, you should use the reload command instead.

## Explanation of directives

To keep our unit files tidy, we haven't littered them with comments. So here we explain the [parameters we've chosen](https://github.com/caddyserver/dist/pull/1):

- **`After=network.target network-online.target`** and **`Requires=network-online.target`** ensures that the network interfaces are online before Caddy starts. This is necessary because Caddy uses the network to obtain certificates and serve your site over TLS. Specifically, `network-online.target` is needed for the many users who bind listeners to specific network interfaces.
- **`TimeoutStopSec=5s`** will forcibly kill the caddy process if it cannot gracefully shut down within this time limit. We figure, if you're stopping the server anyway (as opposed to reloading -- two very distinct operations!) then stopping gracefully is less important than stopping at all.
- **`LimitNOFILE=1048576`** raises the file descriptor limit for the caddy process (`ulimit -n`). This is very important for busy sites, or for servers which need to keep connections open longer. This is the [maximum allowed value](https://stackoverflow.com/a/1213069/1048862) for some popular Linux distros.
- **`LimitNPROC=512`** raises the number of threads caddy is allowed to have (`ulimit -u`). Obviously, setting this too low for a highly concurrent server is a bad idea.
- **`PrivateTmp=true`** keeps /tmp and /var/tmp private, which are discarded after caddy stops.
- **`ProtectSystem=full`** allows writing to /var, which is crucial so that it can store certificates and other data for your site.
- **`AmbientCapabilities=CAP_NET_BIND_SERVICE`** allows caddy to bind to low ports (< 1024) without running as root.
