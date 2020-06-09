#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

requirements = ['feedparser']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Ivan Markeev",
    author_email='markeev@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Wrapper around feedparser.",
    install_requires=requirements,
    include_package_data=True,
    keywords='feedparser_wrapper',
    name='feedparser_wrapper',
    packages=find_packages(include=['feedparser_wrapper', 'feedparser_wrapper.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/markeyev/feedparser_wrapper',
    version='0.1.0',
    zip_safe=False,
)
