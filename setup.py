import os
import re
import sys
from subprocess import check_output
from setuptools import (
    setup,
    find_packages,
)


def read(filename):
    with open(filename) as fp:
        return fp.read()


def fetch_init(key):
    # open the __init__.py file to determine a value instead of importing the package
    return re.search(r'{}\s*=\s*(.+)'.format(key), read(init_original)).group(1).strip('\'\"')


def get_version():
    init_version = fetch_init('__version__')
    if 'dev' not in init_version or testing:
        return init_version

    if 'develop' in sys.argv:
        # then installing in editable (develop) mode
        #   python setup.py develop
        #   pip install -e .
        # following PEP-440, the local version identifier starts with '+'
        return init_version + '+editable'

    # append the commit hash to __version__
    setup_dir = os.path.dirname(os.path.realpath(__file__))
    try:
        # write all error messages from git to devnull
        with open(os.devnull, mode='w') as devnull:
            out = check_output(['git', 'rev-parse', 'HEAD'], cwd=setup_dir, stderr=devnull)
            sha1 = out.strip().decode()
    except:
        # the git executable is not available, manually parse .git directory
        try:
            git_dir = os.path.join(setup_dir, '.git')
            with open(os.path.join(git_dir, 'HEAD'), mode='rt') as fp1:
                line = fp1.readline().strip()
                if line.startswith('ref:'):
                    _, ref_path = line.split()
                    with open(os.path.join(git_dir, ref_path), mode='rt') as fp2:
                        sha1 = fp2.readline().strip()
                else:  # detached HEAD
                    sha1 = line
        except:
            return init_version

    suffix = sha1[:7]
    if not suffix or init_version.endswith(suffix):
        return init_version

    # following PEP-440, the local version identifier starts with '+'
    dev_version = init_version + '+' + suffix

    with open(init_original) as fp:
        init_source = fp.read()

    if os.path.isfile(init_backup):
        os.remove(init_backup)
    os.rename(init_original, init_backup)

    with open(init_original, mode='wt') as fp:
        fp.write(re.sub(
            r'__version__\s*=.+',
            "__version__ = '{}'".format(dev_version),
            init_source
        ))

    return dev_version


# the packages that pr-autocollimator depends on
install_requires = [
    'opencv-python==4.5.4.60',
    'numpy==1.21.4',
    'requests',
    'flask; "arm" in platform_machine',
    'matplotlib; "arm" in platform_machine',
    'picamera; "arm" in platform_machine',
    'rpi-ws281x; "arm" in platform_machine',
    'RPi.GPIO; "arm" in platform_machine',
    'scipy==1.7.3; "arm" in platform_machine',
]

# the packages that are needed for running the tests
tests_require = ['pytest', 'pytest-cov']

testing = {'test', 'tests'}.intersection(sys.argv)

init_original = 'autocollimator/__init__.py'
init_backup = init_original + '.backup'
version = get_version()

setup(
    name='pr-autocollimator',
    version=version,
    author=fetch_init('__author__'),
    author_email='info@measurement.govt.nz',
    url='https://github.com/MSLNZ/pr-autocollimator',
    description='Locate the crosshair of the autocollimator',
    long_description=read('README.rst'),
    platforms='any',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',
    ],
    tests_require=tests_require,
    install_requires=install_requires,
    extras_require={'tests': tests_require},
    entry_points={
        'console_scripts': [
            'autocollimator = autocollimator.webapp:run',
        ],
    },
    packages=find_packages(include=('autocollimator',)),
    include_package_data=True,
)

if os.path.isfile(init_backup):
    os.remove(init_original)
    os.rename(init_backup, init_original)
