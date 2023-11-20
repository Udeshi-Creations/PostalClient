from setuptools import setup, find_packages
import os

VERSION = '0.0.1'
DESCRIPTION = 'Postal API Wrapper for Python'
LONG_DESCRIPTION = 'A package that introduces Postal API for Python.'

# Setting up
setup(
    name="postal-client",
    version=VERSION,
    author="Udeshi Creations (Prem Udeshi)",
    author_email="<info@udeshi.dev>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['python-magic'],
    keywords=['python', 'postal', 'postal client'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)