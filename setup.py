import os
import iblox_kit
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='terraformware',
    version='0.9',
    description='Terraform for VMware and Infoblox',
    url='https://git.geant.net/gitlab/terraform/terraformware',
    author='Massimiliano Adamo',
    author_email='massimiliano.adamo@geant.org',
    license='GPL',
    include_package_data=True,
    scripts=[
        'bin/terraformware',
    ],
    packages=['iblox_kit'] + [os.path.join("iblox_kit", p) for p in find_packages("iblox_kit")],
    zip_safe=False)
