from setuptools import setup

with open('perplex/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            VERSION = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        VERSION = '0.0.1'

with open('README.md', 'r', encoding='utf-8') as f:
    README = f.read()


setup(
    name='perplex',
    version=VERSION,
    description='Perpetual Plex in the Cloud',
    long_description=README,
    long_description_content_type='text/markdown',
    keywords='plex kubernetes cloud storage filesystem',
    url='https://github.com/ofek/perplex',
    author='Ofek Lev',
    author_email='ofekmeister@gmail.com',
    license='MIT/Apache-2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Multimedia',
        'Topic :: System :: Archiving :: Mirroring',
        'Topic :: System :: Filesystems',
        'Topic :: Utilities',
    ],
    packages=['perplex'],
    python_requires='>=3.6',
    install_requires=[
        'appdirs',
        'atomicwrites',
        'binary',
        'click',
        'colorama',
        'docker-compose>=1.23.2',
        'pyperclip>=1.7.0',
        'pytz>=2018.7',
        'PyYAML>=3.13',
        'requests',
        'toml>=0.10.0',
        'tzlocal>=1.5.1',
    ],
    entry_points={'console_scripts': ['perplex = perplex.cli:perplex']},
    include_package_data=True,
)
