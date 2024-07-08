# -*- coding: utf-8 -*-
"""Installer for the imio.helpers package."""

from setuptools import find_packages
from setuptools import setup


long_description = (
    open('README.rst').read() + '\n' + open('CHANGES.rst').read() + '\n')

setup(
    name='imio.helpers',
    version='1.0.0rc4',
    description="Various helper methods for development.",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 6.0",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.10",
    ],
    keywords='plone helpers utils dev imio',
    author='Simon Delcourt',
    author_email='simon.delcourt@imio.be',
    url='https://github.com/imio/imio.helpers',
    download_url='https://pypi.org/project/imio.helpers',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['imio'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'collective.fingerpointing',
        'collective.monkeypatcher',
        'future>=0.18.2',
        'imio.pyutils>=1.0.0',
        'natsort<7',
        "pathlib2;python_version<'3'",
        'plone.api>1.9.1',
        'plone.app.intid',
        'plone.app.relationfield',
        'plone.dexterity',
        'setuptools',
        'six',
        'Plone',
        'z3c.unconfigure',
    ],
    extras_require={
        'test': [
            'collective.behavior.talcondition',
            'collective.MockMailHost',
            'ipdb',
            'plone.app.dexterity',
            'plone.app.testing',
        ],
        'pdf': [
            'PyPDF2',
            'reportlab',
        ],
        'lxml': [
            'cssselect<1.2; python_version == "2.7"',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
