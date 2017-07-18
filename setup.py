from setuptools import setup, find_packages
from time_checks import __version__


def readme():
    with open('README.md') as f:
        return f.read()

reqs = [line.strip() for line in open('requirements.txt')]

GIT_REPO = "https://github.com/cedadev/time-checks"

setup(
    name                 = "time-checks",
    version              = __version__,
    description          = "A set of checks that can be run on individual data files or on groups of data files",
    long_description     = readme(),
    license              = '',
    author               = "Ruth Petrie",
    author_email         = "ruth.petrie@stfc.ac.uk",
    url                  = GIT_REPO,
    packages             = find_packages(),
    install_requires     = reqs,
    tests_require        = ['pytest'],
    classifiers          = [
        'Development Status :: 2 - ???',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: ???',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
    ],
    include_package_data = True,
    scripts=[],
    entry_points = {},
    package_data = {
        'time_checks': ['test/example_data/*'],
    }
)
