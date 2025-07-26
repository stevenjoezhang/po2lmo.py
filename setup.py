#!/usr/bin/env python3
"""
Setup script for po2lmo package
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

# Read version from __init__.py
def read_version():
    version_file = os.path.join('po2lmo', '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return '0.1.0'

setup(
    name='po2lmo',
    version=read_version(),
    author='Shuqiao Zhang',  # 请替换为您的姓名
    author_email='stevenjoezhang@gmail.com',  # 请替换为您的邮箱
    description='Convert GNU gettext PO files to Lua Machine Objects (LMO) binary format',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/stevenjoezhang/po2lmo.py',  # 请替换为您的 GitHub 仓库地址
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Internationalization',
        'Topic :: Software Development :: Localization',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'po2lmo=po2lmo.cli:main',
        ],
    },
    keywords='gettext po lmo lua internationalization localization i18n l10n',
    project_urls={
        'Bug Reports': 'https://github.com/stevenjoezhang/po2lmo.py/issues',
        'Source': 'https://github.com/stevenjoezhang/po2lmo.py',
    },
)
