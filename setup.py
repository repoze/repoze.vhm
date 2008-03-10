__version__ = '0.5'

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()

setup(name='repoze.vhm',
      version=__version__,
      description='repoze virtual hosting middleware.',
      long_description=README,
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Framework :: Zope3",
        ],
      keywords='web application server wsgi zope repoze',
      author="Agendaless Consulting",
      author_email="repoze-dev@lists.repoze.org",
      dependency_links=['http://dist.repoze.org'],
      url="http://www.repoze.org",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['repoze'],
      zip_safe=False,
      test_suite = "repoze.vhm.tests",
      entry_points="""
      [paste.filter_app_factory]
      vhm_xheaders = repoze.vhm.middleware:make_filter
      """,
      )
