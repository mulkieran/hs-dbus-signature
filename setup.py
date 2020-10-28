"""
Python packaging file for setup tools.
"""

# isort: STDLIB
import os

# isort: THIRDPARTY
import setuptools


def local_file(name):
    """
    Function to obtain the relative path of a filename.
    """
    return os.path.relpath(os.path.join(os.path.dirname(__file__), name))


README = local_file("README.rst")

with open(local_file("src/hs_dbus_signature/_version.py")) as o:
    exec(o.read())  # pylint: disable=exec-used

setuptools.setup(
    name="hs-dbus-signature",
    version=__version__,  # pylint: disable=undefined-variable
    author="Anne Mulhern",
    author_email="amulhern@redhat.com",
    url="https://github.com/stratis-storage/hs-dbus-signature",
    description="dbus signature hypothesis strategy generator",
    long_description=open(README, encoding="utf-8").read(),
    platforms=["Linux"],
    license="MPL v2",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Hypothesis",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
    ],
    install_requires=["hypothesis"],
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
)
