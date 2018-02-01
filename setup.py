from setuptools import setup

setup(
    name='timg',
    version='0.3',
    description='Display an image in terminal.',
    url='https://github.com/adzierzanowski/timg',
    author='Aleksander Dzierżanowski',
    author_email='a.dzierzanowski1@gmail.com',
    license='MIT',
    packages=['timg'],
    include_package_data=True,
    install_requires=['pillow'],
    scripts=['bin/timg'],
    zip_safe=False
)

