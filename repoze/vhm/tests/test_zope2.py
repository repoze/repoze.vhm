import unittest

class TestVHM2(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.vhm.zope2 import VHMFilter
        return VHMFilter

    def _makeOne(self, app):
        return self._getTargetClass()(app)

    def test___call___no_markers_unchanged(self):
        # Environments which do not have markers don't get munged.
        expected = {}
        app = VHMTestApp(expected)
        filter = self._makeOne(app)
        REAL_PATH = '/a/b/c/'
        environ = {'wsgi.url_scheme': 'http',
                   'SERVER_NAME': 'example.com',
                   'SERVER_PORT': '8888',
                   'SCRIPT_NAME': '/script',
                   'PATH_INFO': REAL_PATH,
                  }

        filter(environ, noopStartResponse)

        self.assertEqual(expected.get('wsgi.url_scheme'), 'http')
        self.assertEqual(expected['SERVER_NAME'], 'example.com')
        self.assertEqual(expected['SERVER_PORT'], '8888')
        self.assertEqual(expected['SCRIPT_NAME'], '/script')
        self.assertEqual(expected['PATH_INFO'], REAL_PATH)

    def test___call___VirtualHostBase_only_default_port(self):
        # VHB: consume next two tokens, converts to new scheme / netloc.
        #      Note we preserve the port here (elided by 'setServerURL').
        expected = {}
        app = VHMTestApp(expected)
        filter = self._makeOne(app)
        PREFIX = '/VirtualHostBase/http/example.com:80'
        REAL_PATH = '/a/b/c/'
        environ = {'wsgi.url_scheme': 'http',
                   'SERVER_NAME': 'localhost',
                   'SERVER_PORT': '8080',
                   'SCRIPT_NAME': '/script',
                   'PATH_INFO': PREFIX + REAL_PATH,
                  }

        filter(environ, noopStartResponse)

        self.assertEqual(expected['wsgi.url_scheme'], 'http')
        self.assertEqual(expected['SERVER_NAME'], 'example.com')
        self.assertEqual(expected['SERVER_PORT'], '80')
        self.assertEqual(expected['SCRIPT_NAME'], '/script')
        self.assertEqual(expected['PATH_INFO'], REAL_PATH)

    def test___call___VirtualHostBase_only_strange_port(self):
        # VHB: consume next two tokens, converts to new scheme / netloc.
        expected = {}
        app = VHMTestApp(expected)
        filter = self._makeOne(app)
        PREFIX = '/VirtualHostBase/http/example.com:8000'
        REAL_PATH = '/a/b/c/'
        environ = {'wsgi.url_scheme': 'http',
                   'SERVER_NAME': 'localhost',
                   'SERVER_PORT': '8080',
                   'SCRIPT_NAME': '/script',
                   'PATH_INFO': PREFIX + REAL_PATH,
                  }

        filter(environ, noopStartResponse)

        self.assertEqual(expected['SERVER_NAME'], 'example.com')
        self.assertEqual(expected['SERVER_PORT'], '8000')
        self.assertEqual(expected['SCRIPT_NAME'], '/script')
        self.assertEqual(expected['PATH_INFO'], REAL_PATH)

    def test___call___VirtualHostRoot_no_subpath(self):
        # VHR immediately following VHB + 2 -> no vroot.
        expected = {}
        app = VHMTestApp(expected)
        filter = self._makeOne(app)
        REAL_PATH = '/a/b/c/'
        PREFIX = '/VirtualHostBase/https/example.com:443/VirtualHostRoot'
        environ = {'wsgi.url_scheme': 'http',
                   'SERVER_NAME': 'localhost',
                   'SERVER_PORT': '8080',
                   'SCRIPT_NAME': '/script',
                   'PATH_INFO': PREFIX + REAL_PATH,
                  }

        filter(environ, noopStartResponse)

        self.assertEqual(expected['wsgi.url_scheme'], 'https')
        self.assertEqual(expected['repoze.vhm.virtual_root'], '/')
        self.assertEqual(expected['SERVER_NAME'], 'example.com')
        self.assertEqual(expected['SERVER_PORT'], '443')
        self.assertEqual(expected['SCRIPT_NAME'], '/script')
        self.assertEqual(expected['PATH_INFO'], REAL_PATH)

    def test___call___VirtualHostRoot_w_subpath(self):
        # Tokens after VHB + 2, before VHR -> vroot
        expected = {}
        app = VHMTestApp(expected)
        filter = self._makeOne(app)
        REAL_PATH = '/a/b/c/'
        PREFIX = '/VirtualHostBase/http/example.com:80/sub1/VirtualHostRoot'
        environ = {'wsgi.url_scheme': 'http',
                   'SERVER_NAME': 'localhost',
                   'SERVER_PORT': '8080',
                   'SCRIPT_NAME': '/script',
                   'PATH_INFO': PREFIX + REAL_PATH,
                  }

        filter(environ, noopStartResponse)

        self.assertEqual(expected['wsgi.url_scheme'], 'http')
        self.assertEqual(expected['repoze.vhm.virtual_root'], '/sub1')
        self.assertEqual(expected['SERVER_NAME'], 'example.com')
        self.assertEqual(expected['SERVER_PORT'], '80')
        self.assertEqual(expected['SCRIPT_NAME'], '/script')
        self.assertEqual(expected['PATH_INFO'], '/sub1' + REAL_PATH)

    def test___call___VirtualHostRoot__vh__externals(self):
        # special tokens after VHR -> script name ("external" prefix).
        expected = {}
        app = VHMTestApp(expected)
        filter = self._makeOne(app)
        REAL_PATH = '/a/b/c/'
        PREFIX = ('/VirtualHostBase/http/example.com:80/VirtualHostRoot'
                  '/_vh_sub1/_vh_sub2')
        environ = {'wsgi.url_scheme': 'http',
                   'SERVER_NAME': 'localhost',
                   'SERVER_PORT': '8080',
                   'SCRIPT_NAME': '/script',
                   'PATH_INFO': PREFIX + REAL_PATH,
                  }

        filter(environ, noopStartResponse)

        self.assertEqual(expected['wsgi.url_scheme'], 'http')
        self.assertEqual(expected['SERVER_NAME'], 'example.com')
        self.assertEqual(expected['SERVER_PORT'], '80')
        self.assertEqual(expected['SCRIPT_NAME'], '/sub1/sub2')
        self.assertEqual(expected['PATH_INFO'], REAL_PATH)

class Test_setServerURL(unittest.TestCase):

    def _getFUT(self):
        from repoze.vhm.zope2 import setServerURL
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

def noopStartResponse(status, headers):
    pass

class VHMTestApp:
    def __init__(self, _called_environ):
        self._called_environ = _called_environ

    def __call__(self, environ, start_response):
        self._called_environ.clear()
        self._called_environ.update(environ)
        return self.__class__.__name__
