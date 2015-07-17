import codecs
import os
import re
from setuptools import setup, find_packages

with codecs.open(os.path.join(os.path.abspath(os.path.dirname(
        __file__)), 'elasticine', '__init__.py'), 'r', 'latin1') as fp:
    try:
        version = re.findall(r"^__version__ = '([^']+)'\r?$",
                             fp.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')


install_requires = ['elasticsearch', 'pyyaml', 'jinja2']

tests_require = install_requires + ['nose']


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()

setup(
    name='elasticine',
    version=version,
    description=('Elastic migration tool'),
    long_description='\n\n'.join((read('README.rst'), read('CHANGES.rst'))),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Database :: Front-Ends'],
    author='Taras Voinarovskyi',
    author_email='voyn1991@gmail.com',
    url='https://github.com/Drizzt1991/elasticine',
    license='MIT',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='nose.collector',
    zip_safe=False,
    entry_points={
        'console_scripts': ['elasticine = elasticine.cli:main'],
    },
    include_package_data=True)
