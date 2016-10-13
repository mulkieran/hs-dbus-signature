import os
import sys
import setuptools
if sys.version_info[0] < 3:
    from codecs import open

def local_file(name):
    return os.path.relpath(os.path.join(os.path.dirname(__file__), name))

README = local_file("README.rst")

with open(local_file("src/hs_dbus_signature/_version.py")) as o:
        exec(o.read())

setuptools.setup(
    name='hs-dbus-signature',
    version=__version__,
    author='Anne Mulhern',
    author_email='amulhern@redhat.com',
    description='dbus signature hypothesis strategy generator',
    long_description=open(README, encoding='utf-8').read(),
    platforms=['Linux'],
    license='MPL v2',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
        ],
    install_requires = [
        "hypothesis"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages("src")
    )
