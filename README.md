# Terraform for VMware and Infoblox

## how to use the script

Clone the repository:
```sh
git clone gitlab@git.geant.net:terraform/terraformware.git
```

Install the package:
```sh
python setup.py sdist
sudo pip install dist/terraformware-XXX.tar.gz
```

AVOID the installation through setup.py: `sudo python setup.py install`


and run it with --help to check the available options:
```sh
terraformware --help
```

The first time a configuration file will be created: you'll need to fill it with proper values.


The script must be executed within the directory where you have the terraform configuration files: `terraformware.j2` and `variables.tf`


The script will sync the status of your servers. In detail it will:

- render `terraform.j2` and create a terraform file (`main.tf`) using the variables defined in `variables.tf` (`main.tf` will vanish when the script ends)

- add/replace/remove DNS entries to infoblox

- run terraform

- in addition, you can create CNAME and query Infoblox for free IP

## terraform

Download [terraform](https://www.terraform.io/downloads.html)

The version of your terraform can be checked by running: `terraform version` (it will tell you if a newer version is available).

## why not terraform Infoblox provider? 

- it does not work with every version of the API (did not work for me)
- it's not an official Terraform plugin and you need to compile it against your terraform
- this scripts offer few more features, such as CNAME and search for free IP records. 

## Config samples

### variables.tf
```go
# Variables
#
variable "instances" {
  default = "3"
}

variable "common" {
  type = "map"
  default = {
    network = "External"
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
```

### terraformware.j2 (example)
```jinja
# set consul backend
data "terraform_remote_state" "{{ custom_global('MODULE_DIR') }}" {
  backend = "consul"
  config {
    address      = "{{ custom_variable('consul_server') }}"
    access_token = "{{ custom_variable('consul_token') }}"
    datacenter   = "GEANT"
    scheme       = "http"
    path         = "{{ custom_global('MODULE_DIR') }}"
    lock         = "true"
  }
}

# Configure VMware vSphere Provider
provider "vsphere" {
    vsphere_server       = "{{ custom_variable('vsphere_server') }}"
    user                 = "{{ custom_variable('vsphere_username') }}"
    password             = "{{ custom_variable('vsphere_password') }}"
    allow_unverified_ssl = "true"
}

# Create folder "{{ custom_global('MODULE_DIR') }}"
resource "vsphere_folder" "{{ custom_global('MODULE_DIR') }}" {
    datacenter = "${var.common["datacenter"]}"
    path       = "{{ custom_global('MODULE_DIR') }}"
}

{% for count in range(instances|int) -%}
{% set instance = "_" ~ (count + 1)|string -%}

# Create virtual machine {{ custom_dictionary(instance, 'hostname') }} within the folder {{ custom_global('MODULE_DIR') }}
resource "vsphere_virtual_machine" "{{ custom_dictionary(instance, 'hostname') }}" {
    name        = "${var.{{ instance }}["hostname"]}"
    datacenter  = "${var.common["datacenter"]}"
    folder      = "{{ custom_global('MODULE_DIR') }}"
    vcpu        = "${var.{{ instance }}["vcpu"]}"
    memory      = "${var.{{ instance }}["memory"]}"
    dns_servers = "${var.dns_servers}"
    domain      = "${var.{{ instance }}["domain"]}"

    network_interface {
        label              = "${var.{{ instance }}["net_label"]}"
        ipv4_address       = "${var.{{ instance }}["ipv4_address"]}"
        ipv4_gateway       = "${var.{{ instance }}["ipv4_gateway"]}"
        ipv4_prefix_length = "${var.{{ instance }}["ipv4_prefix_length"]}"
        ipv6_address       = "${var.{{ instance }}["ipv6_address"]}"
        ipv6_gateway       = "${var.{{ instance }}["ipv6_gateway"]}"
        ipv6_prefix_length = "${var.{{ instance }}["ipv6_prefix_length"]}"
    }

    /*
    network_interface {
        label   .... (2nd network interface)
    }
    */

    disk {
        datastore = "${var.common["datastore"]}"
        template  = "${var.common["template"]}"
    }

    provisioner "remote-exec" {
        inline = [
          "/bin/sed -i s,PUPPETSERVER,${var.common["puppet_server"]}, ${var.common["puppet_conf"]}",
          "/bin/sed -i s,PUPPETCA,${var.puppet_ca}, ${var.common["puppet_conf"]}",
          "/bin/sed -i s,PUPPETENVIRONMENT,${var.puppet_environment}, ${var.common["puppet_conf"]}",
        ]
    }

}

{% endfor %}
```
