import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="car-connector-framework",
    version="0.0.11",
    author="IBM",
    author_email="",
    description="CAR service connector framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IBM/cp4s-car-connector-framework",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests>=2.24.0', # This is for prod pypi
        # 'requests', # This is for test pypi
    ]
)