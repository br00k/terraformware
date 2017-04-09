# Terraform Template (generated through Jinja template)
#

# Configure Infoblox Provider
provider "infoblox" {
  username  = "${var.iblox_user}"
  password  = "${var.iblox_password}"
  host      = ""
  sslverify = "false"
}

# Configure VMware vSphere Provider
provider "vsphere" {
  vsphere_server       = "${var.common["vsphere_server"]}"
  user                 = "${var.vsphere_user}"
  password             = "${var.vsphere_password}"
  allow_unverified_ssl = "true"
}

# Create a folder
resource "vsphere_folder" "${var.common["folder"]}" {
  datacenter = "${var.common["datacenter"]}"
  path       = "${var.common["folder"]}"
}

# Create A record on Infoblox
resource "infoblox_record" "${lookup(var.1["hostname"])}_A" {
	value = "${lookup(var.1["ipv4_address"])}"
	name = "${element(split(".", lookup(var.1["hostname"])), 0)}"
	domain = "${lookup(var.1["domain"])}"
	type = "A"
	ttl = 3600
}

# Create AAAA record on Infoblox
resource "infoblox_record" "${lookup(var.1["hostname"])}_AAAA" {
	value = "${lookup(var.1["ipv6_address"])}"
	name = "${element(split(".", lookup(var.1["hostname"])), 0)}"
	domain = "${lookup(var.1["domain"])}"
	type = "AAAA"
	ttl = 3600
}

# Create virtual machine within the folder
resource "vsphere_virtual_machine" "${lookup(var.1["hostname"])}" {
  name        = "${lookup(var.1["hostname"]}"
  datacenter  = "${lookup(var.common["datacenter"]}"
  folder      = "${lookup(var.common["folder"]}"
  vcpu        = "${lookup(var.1["vcpu"]}"
  memory      = "${lookup(var.1["memory"]}"
  dns_servers = "${lookup(var.dns_servers})"
  domain      = "${var.1["domain"]}"

  network_interface {
    label              = "${lookup(var.1["label"]})"
    ipv4_address       = "${var.1["ipv4_address"]}"
    ipv4_gateway       = "${var.1["ipv4_gateway"]}"
    ipv4_prefix_length = "${var.1["ipv4_prefix_length"]}"
    ipv6_address       = "${var.1["ipv6_address"]}"
    ipv6_gateway       = "${var.1["ipv6_gateway"]}"
    ipv6_prefix_length = "${var.1["ipv6_prefix_length"]}"
  }

  #network_interface {
  #  label   .... (2nd network interface)
  #}

  disk {
    datastore = "${var.common["datastore"]}"
    template  = "${var.common["template"]}"
  }

  #provisioner "remote-exec" {
  #  inline = [
  #    "/bin/sed -i s,PUPPETSERVER,${var.common["puppet_server"]}, ${var.common["puppet_conf"]}",
  #    "/bin/sed -i s,PUPPETCA,${var.puppet_ca}, ${var.common["puppet_conf"]}",
  #    "/bin/sed -i s,PUPPETENVIRONMENT,${var.puppet_environment}, ${var.common["puppet_conf"]}",
  #  ]
  #}

}

# Create A record on Infoblox
resource "infoblox_record" "${lookup(var.2["hostname"])}_A" {
	value = "${lookup(var.2["ipv4_address"])}"
	name = "${element(split(".", lookup(var.2["hostname"])), 0)}"
	domain = "${lookup(var.2["domain"])}"
	type = "A"
	ttl = 3600
}

# Create AAAA record on Infoblox
resource "infoblox_record" "${lookup(var.2["hostname"])}_AAAA" {
	value = "${lookup(var.2["ipv6_address"])}"
	name = "${element(split(".", lookup(var.2["hostname"])), 0)}"
	domain = "${lookup(var.2["domain"])}"
	type = "AAAA"
	ttl = 3600
}

# Create virtual machine within the folder
resource "vsphere_virtual_machine" "${lookup(var.2["hostname"])}" {
  name        = "${lookup(var.2["hostname"]}"
  datacenter  = "${lookup(var.common["datacenter"]}"
  folder      = "${lookup(var.common["folder"]}"
  vcpu        = "${lookup(var.2["vcpu"]}"
  memory      = "${lookup(var.2["memory"]}"
  dns_servers = "${lookup(var.dns_servers})"
  domain      = "${var.2["domain"]}"

  network_interface {
    label              = "${lookup(var.2["label"]})"
    ipv4_address       = "${var.2["ipv4_address"]}"
    ipv4_gateway       = "${var.2["ipv4_gateway"]}"
    ipv4_prefix_length = "${var.2["ipv4_prefix_length"]}"
    ipv6_address       = "${var.2["ipv6_address"]}"
    ipv6_gateway       = "${var.2["ipv6_gateway"]}"
    ipv6_prefix_length = "${var.2["ipv6_prefix_length"]}"
  }

  #network_interface {
  #  label   .... (2nd network interface)
  #}

  disk {
    datastore = "${var.common["datastore"]}"
    template  = "${var.common["template"]}"
  }

  #provisioner "remote-exec" {
  #  inline = [
  #    "/bin/sed -i s,PUPPETSERVER,${var.common["puppet_server"]}, ${var.common["puppet_conf"]}",
  #    "/bin/sed -i s,PUPPETCA,${var.puppet_ca}, ${var.common["puppet_conf"]}",
  #    "/bin/sed -i s,PUPPETENVIRONMENT,${var.puppet_environment}, ${var.common["puppet_conf"]}",
  #  ]
  #}

}

# Create A record on Infoblox
resource "infoblox_record" "${lookup(var.3["hostname"])}_A" {
	value = "${lookup(var.3["ipv4_address"])}"
	name = "${element(split(".", lookup(var.3["hostname"])), 0)}"
	domain = "${lookup(var.3["domain"])}"
	type = "A"
	ttl = 3600
}

# Create AAAA record on Infoblox
resource "infoblox_record" "${lookup(var.3["hostname"])}_AAAA" {
	value = "${lookup(var.3["ipv6_address"])}"
	name = "${element(split(".", lookup(var.3["hostname"])), 0)}"
	domain = "${lookup(var.3["domain"])}"
	type = "AAAA"
	ttl = 3600
}

# Create virtual machine within the folder
resource "vsphere_virtual_machine" "${lookup(var.3["hostname"])}" {
  name        = "${lookup(var.3["hostname"]}"
  datacenter  = "${lookup(var.common["datacenter"]}"
  folder      = "${lookup(var.common["folder"]}"
  vcpu        = "${lookup(var.3["vcpu"]}"
  memory      = "${lookup(var.3["memory"]}"
  dns_servers = "${lookup(var.dns_servers})"
  domain      = "${var.3["domain"]}"

  network_interface {
    label              = "${lookup(var.3["label"]})"
    ipv4_address       = "${var.3["ipv4_address"]}"
    ipv4_gateway       = "${var.3["ipv4_gateway"]}"
    ipv4_prefix_length = "${var.3["ipv4_prefix_length"]}"
    ipv6_address       = "${var.3["ipv6_address"]}"
    ipv6_gateway       = "${var.3["ipv6_gateway"]}"
    ipv6_prefix_length = "${var.3["ipv6_prefix_length"]}"
  }

  #network_interface {
  #  label   .... (2nd network interface)
  #}

  disk {
    datastore = "${var.common["datastore"]}"
    template  = "${var.common["template"]}"
  }

  #provisioner "remote-exec" {
  #  inline = [
  #    "/bin/sed -i s,PUPPETSERVER,${var.common["puppet_server"]}, ${var.common["puppet_conf"]}",
  #    "/bin/sed -i s,PUPPETCA,${var.puppet_ca}, ${var.common["puppet_conf"]}",
  #    "/bin/sed -i s,PUPPETENVIRONMENT,${var.puppet_environment}, ${var.common["puppet_conf"]}",
  #  ]
  #}

}

