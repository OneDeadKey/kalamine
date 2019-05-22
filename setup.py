from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='kalamine',
    version='0.10.1',
    description='a cross-platform Keyboard Layout Maker',
    long_description=readme,
    url='http://github.com/fabi1cazenave/kalamine',
    author='Fabien Cazenave',
    author_email='fabien@cazenave.cc',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    packages=['kalamine'],
    entry_points={
        'console_scripts': [
            'kalamine = kalamine.cli:make',
            'xkalamine = kalamine.cli_xkb:cli',
        ]
    },
    install_requires=[
        'click',
        'pyyaml',
        'lxml',
    ],
    include_package_data=True,
    zip_safe=False
)
