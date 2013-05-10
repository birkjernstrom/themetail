#!/usr/bin/env python

from setuptools import setup, find_packages


long_description = """
Themetail - Empowers local development of Tictail themes.

An unofficial Tictail command-line tool for automatically synchronizing
local copies of themes to your Tictail store. Along with some added flair
to enable developers and designers to work in their preferred environment
along with their favourite gadgets.
"""


setup(
    name='Themetail',
    version='0.8.0',
    description='Themetail - Empowers local development of Tictail themes.',
    long_description=long_description,
    author='Birk Nilson',
    author_email='birk@tictail.com',
    url='https://github.com/birknilson/themetail',
    packages=find_packages(),
    install_requires=[
        'docopt>=0.6.1',
        'requests>=1.2.0',
        'watchdog>=0.6.0',
    ],
    entry_points={
        'console_scripts': [
            'themetail = themetail.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
