#!/usr/bin/env python

from os.path import exists
from setuptools import setup, find_packages
import versioneer

setup(name='topik',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='A Topic Modeling toolkit',
      url='http://github.com/ContinuumIO/topik/',
      author='Topik development team',
      author_email='msarahan@continuum.io',
      license='BSD',
      keywords='topic modeling lda nltk gensim pattern',
      packages=find_packages(),
      package_data={'topik': ['R/runLDAvis.R']},
      install_requires=list(open('requirements.txt').read().strip().split('\n')),
      entry_points= {
          'console_scripts': ['topik = topik.cli:run']
      },
      long_description=(open('README.md').read() if exists('README.md')
                        else ''), zip_safe=False)
