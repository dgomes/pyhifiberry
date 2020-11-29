from setuptools import setup, find_packages
import pyhifiberry

long_description = open('README.md').read()

setup(
    name='pyhifiberry',
    version=pyhifiberry.__version__,
    license='MIT License',
    url='https://github.com/dgomes/pyhifiberry',
    author='Diogo Gomes',
    author_email='diogogomes@gmail.com',
    description='Python library to interface with Hifiberry OS API.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['pyhifiberry'],
    zip_safe=True,
    platforms='any',
    install_requires=[
        'aiohttp',
      ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
