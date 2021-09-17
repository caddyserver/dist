packer {
  required_plugins {
    digitalocean = {
      version = ">= 1.0.0"
      source  = "github.com/hashicorp/digitalocean"
    }
  }
}

variable "token" {
  type    = string
  default = env("DIGITALOCEAN_TOKEN")
}

# "timestamp" template function replacement
locals { timestamp = regex_replace(timestamp(), "[- TZ:]", "") }

# All locals variables are generated from variables that uses expressions
# that are not allowed in HCL2 variables.
# Read the documentation for locals blocks here:
# https://www.packer.io/docs/templates/hcl_templates/blocks/locals
locals {
  image_name = "marketplace-snapshot-${local.timestamp}"
  ssh_user   = "root"
}

source "digitalocean" "caddy_image" {
  api_token     = var.token
  image         = "ubuntu-20-04-x64"
  region        = "nyc3"
  size          = "s-1vcpu-1gb"
  snapshot_name = local.image_name
  ssh_username  = local.ssh_user
}

build {
  sources = ["source.digitalocean.caddy_image"]

  provisioner "shell" {
    scripts = [
      "scripts/00-base.sh",
      "scripts/10-firewall.sh",
      "scripts/20-caddy.sh"
    ]
  }

  provisioner "file" {
    destination = "/etc/fail2ban/jail.local"
    source      = "files/fail2ban/jail.local"
  }

  provisioner "ansible" {
    galaxy_file   = "ansible/requirements.yml"
    playbook_file = "ansible/ansible-playbook.yml"
    user          = local.ssh_user
  }

  provisioner "shell" {
    scripts = [
      "scripts/50-services.sh",
      "scripts/90-cleanup.sh",
      "scripts/95-prep.sh",
      "scripts/99-img_check.sh"
    ]
  }
}
