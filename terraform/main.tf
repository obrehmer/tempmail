terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}
# Droplet
resource "digitalocean_droplet" "tempmail" {
  image  = var.droplet_image
  name   = "tempmail"
  region = var.droplet_region
  size   = var.droplet_size
  ssh_keys = [
    var.ssh_fingerprint
  ]
}

output "droplet_ip_addresses" {
  value = digitalocean_droplet.tempmail.ipv4_address
}
