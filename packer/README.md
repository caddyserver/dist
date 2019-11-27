Caddy Packer Template
======================

Executing the DigitalOcean builder requires setting 2 variables: `DIGITALOCEAN_TOKEN` as an environment variable, and `caddy_version`.

e.g.

`$ DIGITALOCEAN_TOKEN={your DO API key} packer build -var 'caddy_version=v2.0.0-beta9' do-marketplace-image.json`

The scripts `90-cleanup.sh` and `99-img_check.sh` are from [DO's own repo](https://github.com/digitalocean/marketplace-partners/tree/master/scripts).

The droplet is hardened with these roles:

- [dev-sec.os-hardening](https://github.com/dev-sec/ansible-os-hardening)
- [dev-sec.ssh-hardening](https://github.com/dev-sec/ansible-ssh-hardening)
