from setuptools import setup, find_packages

import krakenforwarder

setup(
    name='krakenforwarder',
    version=krakenforwarder.__version__,
    packages=find_packages(exclude=('tests',)),
    include_package_data=True,
    url='https://github.com/supercuiller/krakenforwarder',
    license='MIT',
    author='Thibaut Castaings, Zao Wu',
    author_email='castaings.t@protonmail.com',
    description='Forwards trades from Kraken.com to TCP port',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    install_requires=[
        'pyzmq',
        'schema',
        'pyyaml',
        'krakenex',
        'requests',
        'python-dateutil'
    ],
)
