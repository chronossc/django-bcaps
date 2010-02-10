import os
from distutils.core import setup

setup(
    name = 'django-bcaps',
    version = '0.1 alpha',
    description = 'Easy browser data provided by Broser Capabilities Project',
    author = 'Felipe Prenholato',
    author_email = 'philipe.rp@gmail.com',
    url = 'https://code.google.com/p/django-bcaps/',
    packages = ['bcaps'],
    classifiers = ['Development Status :: 0 - Alpha',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: MIT',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
)
