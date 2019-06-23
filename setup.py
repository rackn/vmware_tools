import os
from setuptools import setup
from setuptools import find_packages


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as fn:
        return fn.read()


with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name='drpy',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    long_description=read('README.rst'),
    url='https://github.com/rackn',
    license='proprietary',
    author='RackN',
    author_email='eng@rackn.com',
    install_requires=required,
    description='Digital Rebar Python'
)
