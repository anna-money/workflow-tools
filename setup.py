import os
import re

from setuptools import find_packages, setup

BASE_DIR = os.path.dirname(os.path.realpath(__file__))


def _refine_description(desc):
    desc = re.sub(r".. raw::.*", "", desc)
    desc = re.sub(r"<img .*", "", desc)
    return desc


def readme():
    long_description = ""
    with open(os.path.join(BASE_DIR, "README.rst")) as f:
        long_description += f.read()

    long_description += "\n\n"
    with open(os.path.join(BASE_DIR, "CHANGELOG.rst")) as f:
        long_description += f.read()

    long_description = _refine_description(long_description)
    return long_description


def get_version():
    version = {}
    with open("version.py") as fp:
        exec(fp.read(), version)
    return version["__version__"]


setup(
    name="workflow_tools",
    description="CLI tools for GitHub Actions",
    long_description=readme(),
    long_description_content_type="text/x-rst",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Unix",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
        "Environment :: MacOS X",
        "Topic :: Internet",
    ],
    author="Absolutely No Nonsense Admin Ltd.",
    author_email="hello@anna.money",
    url="https://github.com/anna-money/workflow-tools",
    license="Apache License 2.0",
    version=get_version(),
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4",
    zip_safe=True,
    include_package_data=True,
    packages=find_packages(exclude=["tests"]),
    install_requires=["Jinja2>=2.11.1", "Click>=7.0,<8.0", "PyNaCl>=1.3.0,<2.0", "requests>=2.22.0,<3.0"],
    entry_points={
        "console_scripts": [
            "workflow_generator = workflow_tools.cli:generator",
            "workflow_secret = workflow_tools.cli:secret",
        ]
    },
)
