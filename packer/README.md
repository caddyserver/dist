Caddy Packer Template for DigitalOcean Image
============================================

This helps build the DigitalOcean droplet image for their marketplace.

## Requirements

- Packer 1.6 or newer
- Ansible

To run the script:

```bash
packer init
DIGITALOCEAN_TOKEN=foobar packer build do-marketplace-image.pkr.hcl
```

Be sure to replace `foobar` with your DigitalOcean API key.

The scripts `90-cleanup.sh` and `99-img_check.sh` are from [DO's own repo](https://github.com/digitalocean/marketplace-partners/tree/master/scripts).

The droplet is hardened with these roles:

- [dev-sec.os-hardening](https://github.com/dev-sec/ansible-os-hardening)
- [dev-sec.ssh-hardening](https://github.com/dev-sec/ansible-ssh-hardening)
