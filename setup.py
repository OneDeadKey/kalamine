from setuptools import setup

setup(name='kalamine',
      version='0.1',
      description='Keyboard Layout Maker',
      url='http://github.com/fabi1cazenave/kalamine',
      author='Fabien Cazenave',
      author_email='fabien@cazenave.cc',
      license='MIT',
      packages=['kalamine'],
      scripts=['bin/kalamine'],
      include_package_data=True,
      zip_safe=False)
