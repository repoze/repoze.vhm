import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
def _read_file(filename):
    try:
        with open(os.path.join(here, filename)) as f:
            return f.read()
    except IOError:  # Travis???
        return ''
README = _read_file('README.rst')
CHANGES = _read_file('CHANGES.rst')

testing_extras = ['nose', 'coverage']

setup(name='repoze.vhm',
      version='0.15',
      description='repoze virtual hosting middleware.',
      long_description=README + CHANGES,
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        ],
      keywords='web application server wsgi zope repoze',
      author="Agendaless Consulting",
      author_email="repoze-dev@lists.repoze.org",
      url="http://www.repoze.org",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['repoze'],
      install_requires=['setuptools', 'six'],
      zip_safe=False,
      test_suite = "repoze.vhm.tests",
      entry_points="""
      [paste.filter_app_factory]
      vhm_xheaders = repoze.vhm.middleware:make_filter
      vhm_explicit = repoze.vhm.middleware:make_explicit_filter
      vhm_path = repoze.vhm.middleware:make_path_filter
      """,
      extras_require = {
        'testing': testing_extras,
      },
)
