from setuptools import setup
from src.timg import version

setup(
  name=version.TIMG_PROG_NAME,
  version=version.TIMG_VERSION,
  description=version.TIMG_DESC,
  url='https://github.com/adzierzanowski/timg',
  author='Aleksander Dzierżanowski',
  author_email='a.dzierzanowski1@gmail.com',
  license='MIT',
  packages=['timg', 'timg/methods'],
  package_dir={'': 'src'},
  include_package_data=True,
  install_requires=['pillow'],
  scripts=['bin/timg'],
  zip_safe=False
)
