import os
import iblox_kit
from glob import glob
from distutils.dir_util import remove_tree
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='terraformware',
    version='0.9.1',
    description=("Tool for managing server status on Terraform and Infoblox"),
    long_description=read('README.md'),
    url='https://git.geant.net/gitlab/terraform/terraformware',
    author='Massimiliano Adamo',
    author_email='massimiliano.adamo@geant.org',
    license='GPL',
    include_package_data=True,
    scripts=['bin/terraformware'],
    packages=['iblox_kit'] + [os.path.join("iblox_kit", p) for p in find_packages("iblox_kit")],
    zip_safe=False
    )

for cleanup in ['dist', 'build', 'terraformware.egg-info']:
    if os.access(cleanup, os.W_OK):
        remove_tree(cleanup, verbose=1, dry_run=0)

print "removing stale bytecode"
for pyc in glob('iblox_kit/*.pyc'):
    os.unlink(pyc)
