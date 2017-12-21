#!/usr/bin/env python
from setuptools import setup, find_packages
import web_cache


setup(
    name='web_cache',
    version=web_cache.__version__,
    description=web_cache.__description__,
    author=web_cache.__author__,
    author_email='pna.dev@outlook.com',
    license=web_cache.__license__,
    url='http://github.com/ilpan/web_cache',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'wcache = web_cache.main:main',
        ],
    },

    install_requires=['redis'],
    python_requires = '>=3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3 :: Only',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Software Development',
        'Topic :: System :: Networking',
        'Topic :: Terminals',
        'Topic :: Utilities',
    ],
    keywords='web_cache http python3',
)
