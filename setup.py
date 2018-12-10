import re
import setuptools

from os import path

base_dir = path.abspath(path.dirname(__file__))

with open(path.join(base_dir, 'README.md')) as f:
    long_description = f.read()

with open(path.join(base_dir, 'qt_actor', '__init__.py')) as f:
    version = re.search("^__version__ = '(?P<version>.*)'$",
                        f.read(),
                        re.MULTILINE).group('version')

setuptools.setup(
    name='qt-actor',
    version=version,
    author='heartsucker',
    author_email='heartsucker@autistici.org',
    url='https://github.com/heartsucker/qt-actor',
    description='Actor systems for Qt',
    long_description=long_description,
    long_description_content_type='text/markdown',
    platforms='any',
    python_requires='>=3.5',
    package_dir={'qt_actor': 'qt_actor'},
    packages=['qt_actor'],
    install_requires=[
        'PyQt5',
    ],
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ),
)
