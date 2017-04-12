# Variables
#
variable "instances" {
  default = "3"
}

variable "common" {
  type = "map"
  default = {
    vsphere_server = "chvc01.win.dante.org.uk"
    datacenter = "CityHouse"
    datastore = "datastore1"
    puppet_server = "puppet01.geant.net"
    puppet_ca = "puppet01.geant.net"
    puppet_conf = "/etc/puppetlabs/puppet/puppet.conf"
    template = "packer-centos-6"
  }
}

variable "dns_servers" {
  type = "list"
  default = ["62.40.119.100", "62.40.120.134"]
}

variable "_1" {
  type = "map"
  default = {
    hostname = "test-terraform01.geant.net"
    domain = "geant.net"
    net_label = "GEANT"
    ipv4_address = "192.168.1.200"
    ipv4_gateway = "192.168.1.1"
    ipv4_prefix_length = "24"
    ipv6_address = "fe80::8946:1ea3:9bd4:2787"
    ipv6_gateway = "fe80::"
    ipv6_prefix_length = "64"
    puppet_environment = "test"
    memory = "8192"
    vcpu = "2"
  }
}

variable "_2" {
  type = "map"
  default = {
    hostname = "uat-terraform01.geant.net"
    domain = "geant.net"
    net_label = "GEANT"
    ipv4_address = "192.168.1.201"
    ipv4_gateway = "192.168.1.1"
    ipv4_prefix_length = "24"
    ipv6_address = "fe80::8946:1ea3:9bd4:2788"
    ipv6_gateway = "fe80::"
    ipv6_prefix_length = "64"
    puppet_environment = "uat"
    memory = "8192"
    vcpu = "2"
  }
}

variable "_3" {
  type = "map"
  default = {
    hostname = "prod-terraform01.geant.net"
    domain = "geant.net"
    net_label = "GEANT"
    ipv4_address = "192.168.1.202"
    ipv4_gateway = "192.168.1.1"
    ipv4_prefix_length = "24"
    ipv6_address = "fe80::8946:1ea3:9bd4:2789"
    ipv6_gateway = "fe80::"
    ipv6_prefix_length = "64"
    puppet_environment = "production"
    memory = "8192"
    vcpu = "2"
  }
}
