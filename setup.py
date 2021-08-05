"""
Python packaging file for setup tools.
"""

# isort: THIRDPARTY
import setuptools

setuptools.setup(
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
)
