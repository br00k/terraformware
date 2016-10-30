# Specify the provider and access details
provider "vsphere" {
  user                 = "massimiliano.adamo"
  password             = "<password>"
  vsphere_server       = "vsphereit.win.dante.org.uk"
  allow_unverified_ssl = true
}

# resource to create
resource "vsphere_virtual_machine" "default" {
    name = "test-vm"
    datacenter = "datacenter1"
    cluster = "splunk-esxi.fra.de.geant.net"
    vcpu = 2
    memory = 4096
    disk {
        datastore = "datastore1"
        template = "templates/centos-6.6-x86_64"
    }
    gateway = "192.168.0.1"
    network_interface {
        label = "eth0"
        ip_address = "192.168.0.100"
        subnet_mask = "255.255.255.0"
    }
}
