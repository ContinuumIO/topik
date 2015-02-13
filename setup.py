#!/usr/bin/env python

from os.path import exists
from setuptools import setup, find_packages

setup(name='topik',
      version='0.1.0',
      description='A Topic Modeling toolkit',
      url='http://github.com/ContinuumIO/topik/',
      author='Christine Doig',
      author_email='christine.doig@continuum.io',
      license='BSD',
      keywords='topic modeling lda nltk gensim pattern',
      packages=find_packages(),
      install_requires=list(open('requirements.txt').read().strip().split('\n')),
      entry_points= {
          'console_scripts': ['topik = topik.cli:run']
      },
      long_description=(open('README.md').read() if exists('README.md')
                        else ''), zip_safe=False)
