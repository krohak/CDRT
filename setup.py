import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="LWWElementGraph",
    version="1.0.5",
    description="Module for a lightweight LWWElementGraph",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/krohak/CDRT",
    author="krohak",
    author_email="rohaksinghal14@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
)