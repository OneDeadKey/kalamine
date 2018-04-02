from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='kalamine',
    version='0.2.3',
    description='a yaml-centric Keyboard Layout Maker',
    long_description=readme,
    url='http://github.com/fabi1cazenave/kalamine',
    author='Fabien Cazenave',
    author_email='fabien@cazenave.cc',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    packages=['kalamine'],
    scripts=['bin/kalamine'],
    install_requires=['pyyaml'],
    include_package_data=True,
    zip_safe=False
)
