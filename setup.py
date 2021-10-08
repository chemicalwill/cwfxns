import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='cwfxns',
    version='0.0.1',
    entry_points={
        'console_scripts': [
                'cwfxns = cwfxns',
            ],
        },
    author="Will Hedges",
    author_email="chemicalwill92@gmail.com",
    license="MIT",
    description="Module for personal helper functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chemicalwill/cwfxns",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS-Independent",
    ],
    zip_safe=False
)