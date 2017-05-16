import os
import iblox_kit
from glob import glob
from distutils.dir_util import remove_tree
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='terraformware',
    version='0.9.4',
    description=("Tool for managing server status on Terraform and Infoblox"),
    long_description="long description: cf. http://stackoverflow.com/a/761847",
    url='https://github.com/maxadamo/terraformware',
    install_requires=[
        'pyhcl',
        'infoblox-client',
        'python-terraform',
        'ast',
        'requests',
        'configparser',
        'jinja2'
        ],
    author='Massimiliano Adamo',
    author_email='massimiliano.adamo@geant.org',
    license='GPL',
    scripts=glob('bin/*'),
    packages=['iblox_kit'],
    zip_safe=False
    )

#for cleanup in ['dist', 'build', 'terraformware.egg-info']:
#    if os.access(cleanup, os.W_OK):
#        remove_tree(cleanup, verbose=1, dry_run=0)
#
#print "removing stale bytecode"
#for pyc in glob('iblox_kit/*.pyc'):
#    os.unlink(pyc)
