##############################################################################
#
# Copyright (c) 2008 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

import unittest

class Test_setServerURL(unittest.TestCase):

    def _getFUT(self):
        from repoze.vhm.utils import setServerURL
        return setServerURL

    def test_empty(self):
        setServerURL = self._getFUT()
        environ = {}
        setServerURL(environ)

        self.assertEqual(environ,
                         {'SERVER_URL': 'http://localhost:8080'})

    def test_without_url_scheme(self):
        setServerURL = self._getFUT()
        environ = {'wsgi.url_scheme': 'http',
                   'SERVER_NAME': 'example.com',
                   'SERVER_PORT': '8000',
                   'SCRIPT_NAME': '/script',
                  }
        setServerURL(environ)

        self.assertEqual(environ['SERVER_URL'],
                         'http://example.com:8000')

    def test_with_default_port(self):
        setServerURL = self._getFUT()
        environ = {'wsgi.url_scheme': 'http',
                   'SERVER_NAME': 'example.com',
                   'SERVER_PORT': '80',
                   'SCRIPT_NAME': '/script',
                  }
        setServerURL(environ)

        self.assertEqual(environ['SERVER_URL'],
                         'http://example.com')

    def test_with_alternate_port(self):
        setServerURL = self._getFUT()
        environ = {'wsgi.url_scheme': 'https',
                   'SERVER_NAME': 'example.com',
                   'SERVER_PORT': '4433',
                   'SCRIPT_NAME': '/script',
                  }
        setServerURL(environ)

        self.assertEqual(environ['SERVER_URL'],
                         'https://example.com:4433')

    def test_https_without_url_scheme_with_default_port(self):
        # In case of a PEP 333 violation.
        setServerURL = self._getFUT()
        environ = {'HTTPS': 'on',
                   'SERVER_NAME': 'example.com',
                   'SERVER_PORT': '443',
                   'SCRIPT_NAME': '/script',
                  }
        setServerURL(environ)

        self.assertEqual(environ['SERVER_URL'],
                         'https://example.com')

    def test_with_http_host_has_port(self):
        setServerURL = self._getFUT()
        environ = {'SERVER_NAME': 'example.com',
                   'SERVER_PORT': '8081',
                   'SCRIPT_NAME': '/script',
                   'HTTP_HOST':'localhost:8080',
                  }
        setServerURL(environ)
        self.assertEqual(environ['SERVER_URL'], 'http://localhost:8080')
        
    def test_with_http_host_has_default_port(self):
        setServerURL = self._getFUT()
        environ = {'SERVER_NAME': 'example.com',
                   'SERVER_PORT': '80',
                   'SCRIPT_NAME': '/script',
                   'HTTP_HOST':'localhost:80',
                  }
        setServerURL(environ)
        self.assertEqual(environ['SERVER_URL'], 'http://localhost')

    def test_with_http_host_no_port(self):
        setServerURL = self._getFUT()
        environ = {'SERVER_NAME': 'example.com',
                   'SERVER_PORT': '8081',
                   'SCRIPT_NAME': '/script',
                   'HTTP_HOST':'localhost',
                  }
        setServerURL(environ)
        self.assertEqual(environ['SERVER_URL'], 'http://localhost')

    def test_vhm_host_base_trumps_http_host(self):
        setServerURL = self._getFUT()
        environ = {'SERVER_NAME': 'example.com',
                   'SERVER_PORT': '8081',
                   'SCRIPT_NAME': '/script',
                   'HTTP_HOST':'localhost:8080',
                   'repoze.vhm.virtual_host_base':'www.example.com:80',
                  }
        setServerURL(environ)
        self.assertEqual(environ['SERVER_URL'], 'http://www.example.com')

    def test_vhm_host_base_no_port(self):
        setServerURL = self._getFUT()
        environ = {'SERVER_NAME': 'example.com',
                   'SERVER_PORT': '8081',
                   'SCRIPT_NAME': '/script',
                   'HTTP_HOST':'localhost:8080',
                   'repoze.vhm.virtual_host_base':'www.example.com',
                  }
        setServerURL(environ)
        self.assertEqual(environ['SERVER_URL'], 'http://www.example.com')

class Test_getVirtualRoot(unittest.TestCase):
    def _callFUT(self, environ):
        from repoze.vhm.utils import getVirtualRoot
        return getVirtualRoot(environ)

    def test_without_virtual_root(self):
        environ = {}
        self.assertEqual(self._callFUT(environ), None)

    def test_with_virtual_root(self):
        environ = {'repoze.vhm.virtual_root':'/abc'}
        self.assertEqual(self._callFUT(environ), '/abc')

class Test_getVirtualURL(unittest.TestCase):
    def _callFUT(self, environ):
        from repoze.vhm.utils import getVirtualURL
        return getVirtualURL(environ)

    def test_without_virtual_root(self):
        environ = {}
        self.assertEqual(self._callFUT(environ), None)

    def test_with_virtual_root(self):
        environ = {'repoze.vhm.virtual_url':'/a/b/c'}
        self.assertEqual(self._callFUT(environ), '/a/b/c')
