variable "do_token" {
  description = "DigitalOcean API token"
}
variable "ssh_fingerprint" {
  description = "Fingerprint of your SSH key"
}
variable "droplet_image" {
  description = "Image identifier of the OS in DigitalOcean"
  default     = "ubuntu-24-04-x64"
}
variable "droplet_region" {
  description = "Droplet region identifier where the droplet will be created"
  default     = "lon1"
}
variable "droplet_size" {
  description = "Droplet size identifier"
  default     = "s-1vcpu-1gb"
}
