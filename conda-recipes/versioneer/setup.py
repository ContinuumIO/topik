from distutils.core import setup
import versioneer

setup(name='test',
      description='test',
      author='test',
      author_email='test',
      url='test',
      packages=[],
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
     )
