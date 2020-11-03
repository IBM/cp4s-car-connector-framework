import setuptools
import os
import sys

with open("README.md", "r") as fh:
    long_description = fh.read()

#Prepare requires list
install_requires_list = set()
with open('requirements.txt') as f:
    lines = f.readlines()
lines = [x.strip() for x in lines]
lines = list(filter(lambda s: (not s.startswith('#')) and len(s)>0, lines))
lines = list(filter(lambda s: (not s.startswith('git+')) and len(s)>0, lines))
install_requires_list.update(lines)
install_requires_list = list(install_requires_list)

version = os.environ.get('PYPI_PACKAGE_VERSION')

sys.exit(1)

setuptools.setup(
    name="car-connector-framework",
    version="0.0.16",
    author="IBM",
    author_email="",
    description="CAR service connector framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IBM/cp4s-car-connector-framework",
    packages=setuptools.find_packages(exclude=['tests']),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=install_requires_list,
    license='Apache License 2.0',
    platforms=["Any"]
)