import os

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pymongo',
    'pyramid',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'pystache',
    'waitress',
    ]

setup(name='see_stats',
      version='0.0',
      description='see_stats',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="see_stats",
      entry_points="""\
      [paste.app_factory]
      main = see_stats:main
      """,
      )
