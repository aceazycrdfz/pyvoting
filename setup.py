import codecs
import os
from setuptools import setup, find_packages

# these things are needed for the README.md show on pypi (if you dont need delete it)
here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

# you need to change all these
VERSION = '1.0.0'
DESCRIPTION = 'an election framework that simulates 9 voting methods, including 4 I have invented'
LONG_DESCRIPTION = 'an election framework that simulates 9 voting methods, including 4 I have invented'

setup(
    name="pyvoting",
    version=VERSION,
    author="Yichen Zhang",
    author_email="zycrdfz@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=["pandas", "numpy"],
    keywords=["python", "vote", "voting", "election", "approval voting",
              "star voting", "ranked choice voting", "rcv", "tier list"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
