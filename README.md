# Terraform for VMware and Infoblox

## how to use the script

Clone this repo, install the package and run the help:
```bash
git clone gitlab@git.geant.net:terraform/terraformware.git
sudo python setup.py install
terraformware -h
```

The first time a configuration file will be created: you need to fill in proper values

check `samples/terraformware.j2` and `samples/variables.tf`

The script must be executed within the directory where you have the terraform configuration files


The script will sync the status of your servers. In detail it will:

- render `terraform.j2` and create a terraform file (`main.tf`) using the variables defined in `variables.tf` (`main.tf` will vanish when the script ends)

- add/replace/remove DNS entries to infoblox

- run terraform

## how to use terraform

Download [terraform](https://www.terraform.io/downloads.html)

The version of your terraform can be checked running: `terraform version` (it will tell you if a newer version is available).

## how to use terraform Infoblox provider (Broken!! API version mismatch with our Infoblox version)
#### this task is actually carried out through the python API and this section can be ignored

Download [terraform infoblox provider](https://github.com/prudhvitella/terraform-provider-infoblox/releases/)

Copy the binary somewhere, for instance  `/usr/local/bin/terraform-provider-infoblox`

create the file `~/.terraformrc` with following content:

```
providers {
    infoblox = "/usr/local/bin/terraform-provider-infoblox"
}
```
