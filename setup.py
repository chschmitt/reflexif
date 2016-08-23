from setuptools import setup
from codecs import open


with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name="reflexif",
    packages=['reflexif'],
    version="0.1.0.dev2",
    author="Christoph Schmitt",
    author_email="dev@chschmitt.de",
    description="A library to read, inspect and modify Exif data entirely written in Python",
    long_description=readme,
    license="BSD License",
    package_data={'': ['LICENSE']},
    include_package_data=True,
    keywords="exif",
    url="https://github.com/chschmitt/reflexif",
    package_dir={'reflexif': 'reflexif'},
    test_suite="tests",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: CPython"
    ]
)
