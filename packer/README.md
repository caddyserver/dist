Caddy Packer Template for DigitalOcean Image
============================================

Executing the DigitalOcean builder requires setting 2 variables: `DIGITALOCEAN_TOKEN` as an environment variable, and `caddy_version`.

First make sure you have the latest tags from the `caddyserver/caddy` repo (`git fetch --tags`).

Then you can get the Caddy version with a command, and run the script:

```bash
DIGITALOCEAN_TOKEN=foobar packer build do-marketplace-image.json
```

Be sure to replace:

- Your DigitalOcean API key

The scripts `90-cleanup.sh` and `99-img_check.sh` are from [DO's own repo](https://github.com/digitalocean/marketplace-partners/tree/master/scripts).

The droplet is hardened with these roles:

- [dev-sec.os-hardening](https://github.com/dev-sec/ansible-os-hardening)
- [dev-sec.ssh-hardening](https://github.com/dev-sec/ansible-ssh-hardening)
