from setuptools import setup

from timg import meta


with open('README.md', 'r') as f:
  long_description = f.read()

setup(
  name=meta.NAME,
  version=meta.VERSION,
  description=meta.DESC,
  long_description=long_description,
  long_description_content_type='text/markdown',
  url='https://github.com/adzierzanowski/timg',
  author='Aleksander Dzierżanowski',
  author_email='a.dzierzanowski1@gmail.com',
  license='MIT',
  packages=['timg', 'timg/methods'],
  include_package_data=True,
  install_requires=['pillow'],
  entry_points={
    'console_scripts': [
      'timg = timg.__main__:main'
    ]
  },
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3',
    'Topic :: Multimedia :: Graphics :: Viewers',
  ],
  zip_safe=False
)
