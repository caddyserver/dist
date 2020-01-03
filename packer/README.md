Caddy Packer Template for DigitalOcean Image
============================================

Executing the DigitalOcean builder requires setting 2 variables: `DIGITALOCEAN_TOKEN` as an environment variable, and `caddy_version`.

First make sure you have the latest tags from the `caddyserver/caddy` repo (`git fetch --tags`).

Then you can get the Caddy version with a command, and run the script:

```bash
export CADDY_VERSION=$(git -C ../../caddy describe --abbrev=0 --tags HEAD)
DIGITALOCEAN_TOKEN=foobar packer build -var caddy_version=$CADDY_VERSION do-marketplace-image.json
```

Be sure to replace:
- The `-C` flag with the actual path to your copy of the caddy repository (or just set the caddy_version variable manually, like `-var 'caddy_version=v2.0.0-beta9'`)
- Your DigitalOcean API key

The scripts `90-cleanup.sh` and `99-img_check.sh` are from [DO's own repo](https://github.com/digitalocean/marketplace-partners/tree/master/scripts).

The droplet is hardened with these roles:

- [dev-sec.os-hardening](https://github.com/dev-sec/ansible-os-hardening)
- [dev-sec.ssh-hardening](https://github.com/dev-sec/ansible-ssh-hardening)
