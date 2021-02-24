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


with open(local_file("src/hs_dbus_signature/_version.py")) as o:
    exec(o.read())  # pylint: disable=exec-used

setuptools.setup(
    version=__version__,  # pylint: disable=undefined-variable
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
)
