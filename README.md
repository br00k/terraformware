# Terraform for VMware and Infoblox

This script will:

- render `terraform.j2` and create a terraform file (`main.tf`) using the variables defined in `variables.tf` (this file will vanish when the script ends)

- add/replace/remove DNS entries to infoblox

- run terraform

## how to use terraform

Download [terraform](https://www.terraform.io/downloads.html)

The version of your terraform can be checked running: `terraform version` (it will tell you if a newer version is available).

## how to use terraform Infoblox provider (Broken!!! API mismatch with our Infoblox!!)
### This is actually carried out by the python API

Download [terraform infoblox provider](https://github.com/prudhvitella/terraform-provider-infoblox/releases/)

Copy the binary somewhere, for instance  `/usr/local/bin/terraform-provider-infoblox`

create the file `~/.terraformrc` with following content:

```
providers {
    infoblox = "/usr/local/bin/terraform-provider-infoblox"
}
```

## how to use the script

Help your self with the following libraries:
`os`
`ast`
`glob`
`json`
`argparse`
`ConfigParser`
`hcl` (available throuth pip with the name: `pyhcl`)
`infoblox-client` (available through pip)
`jinja2`
`python-terraform`  (available through pip)
`requests`

## TODO
- add selection for External/Internal view for Infoblox (now we've hardcoded External)

