from setuptools import setup
from src import version

setup(
  name=version.TIMG_PROG_NAME,
  version=version.TIMG_VERSION,
  description=version.TIMG_DESC,
  url='https://github.com/adzierzanowski/timg',
  author='Aleksander Dzierżanowski',
  author_email='a.dzierzanowski1@gmail.com',
  license='MIT',
  packages=['src', 'src/methods'],
  include_package_data=True,
  install_requires=['pillow'],
  scripts=['bin/timg'],
  zip_safe=False
)
