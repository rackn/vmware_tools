from setuptools import setup
from setuptools import find_packages

setup(
    name='drpy',
    version='0.1',

    packages=find_packages(where='src'),
    package_dir={'': 'src'},

    url='https://github.com/rackn',
    license='proprietary',
    author='RackN',
    author_email='eng@rackn.com',
    description='Digital Rebar Python'
)
