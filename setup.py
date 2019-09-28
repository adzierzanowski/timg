from setuptools import setup

from src.timg import meta 


setup(
  name=meta.TIMG_PROG_NAME,
  version=meta.TIMG_VERSION,
  description=meta.TIMG_DESC,
  url='https://github.com/adzierzanowski/timg',
  author='Aleksander Dzierżanowski',
  author_email='a.dzierzanowski1@gmail.com',
  license='MIT',
  packages=['timg', 'timg/methods'],
  package_dir={'': 'src'},
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

