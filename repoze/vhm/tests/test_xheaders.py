import unittest

class TestXHeaders(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.vhm.xheaders import VHMFilter
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
                   'SCRIPT_NAME': '/',
                   'PATH_INFO': REAL_PATH,
                  }

        filter(environ, noopStartResponse)

        self.assertEqual(expected.get('wsgi.url_scheme'), 'http')
        self.assertEqual(expected['SERVER_NAME'], 'example.com')
        self.assertEqual(expected['SERVER_PORT'], '8888')
        self.assertEqual(expected['SCRIPT_NAME'], '/')
        self.assertEqual(expected['PATH_INFO'], REAL_PATH)
        self.assertEqual(expected.get('repoze.vhm.virtual_root'), None)

    def test___call___X_VHM_HOST_only_explicit_port(self):
        expected = {}
        app = VHMTestApp(expected)
        filter = self._makeOne(app)
        REAL_PATH = '/a/b/c/'
        X_VHM_HOST = 'http://example.com:80/script'
        environ = {'wsgi.url_scheme': 'http',
                   'SERVER_NAME': 'localhost',
                   'SERVER_PORT': '8080',
                   'SCRIPT_NAME': '/',
                   'PATH_INFO': REAL_PATH,
                   'HTTP_X_VHM_HOST': X_VHM_HOST,
                  }

        filter(environ, noopStartResponse)

        self.assertEqual(expected['wsgi.url_scheme'], 'http')
        self.assertEqual(expected['SERVER_NAME'], 'example.com')
        self.assertEqual(expected['SERVER_PORT'], '80')
        self.assertEqual(expected['SCRIPT_NAME'], '/script')
        self.assertEqual(expected['PATH_INFO'], REAL_PATH)

    def test___call___X_VHM_HOST_only_default_port(self):
        expected = {}
        app = VHMTestApp(expected)
        filter = self._makeOne(app)
        REAL_PATH = '/a/b/c/'
        X_VHM_HOST = 'http://example.com:80/script'
        environ = {'wsgi.url_scheme': 'http',
                   'SERVER_NAME': 'localhost',
                   'SERVER_PORT': '8080',
                   'SCRIPT_NAME': '/',
                   'PATH_INFO': REAL_PATH,
                   'HTTP_X_VHM_HOST': X_VHM_HOST,
                  }

        filter(environ, noopStartResponse)

        self.assertEqual(expected['wsgi.url_scheme'], 'http')
        self.assertEqual(expected['SERVER_NAME'], 'example.com')
        self.assertEqual(expected['SERVER_PORT'], '80')
        self.assertEqual(expected['SCRIPT_NAME'], '/script')
        self.assertEqual(expected['PATH_INFO'], REAL_PATH)
        self.assertEqual(expected.get('repoze.vhm.virtual_root'), None)

    def test___call___X_VHM_ROOT(self):
        expected = {}
        app = VHMTestApp(expected)
        filter = self._makeOne(app)
        REAL_PATH = '/a/b/c/'
        X_VHM_ROOT = '/a/b'
        environ = {'wsgi.url_scheme': 'http',
                   'SERVER_NAME': 'localhost',
                   'SERVER_PORT': '8080',
                   'SCRIPT_NAME': '/',
                   'PATH_INFO': REAL_PATH,
                   'HTTP_X_VHM_ROOT': X_VHM_ROOT,
                  }

        filter(environ, noopStartResponse)

        self.assertEqual(expected.get('wsgi.url_scheme'), 'http')
        self.assertEqual(expected['SERVER_NAME'], 'localhost')
        self.assertEqual(expected['SERVER_PORT'], '8080')
        self.assertEqual(expected['SCRIPT_NAME'], '/')
        self.assertEqual(expected['PATH_INFO'], REAL_PATH)
        self.assertEqual(expected.get('repoze.vhm.virtual_root'), '/a/b')

def noopStartResponse(status, headers):
    pass

class VHMTestApp:
    def __init__(self, _called_environ):
        self._called_environ = _called_environ

    def __call__(self, environ, start_response):
        self._called_environ.clear()
        self._called_environ.update(environ)
        return self.__class__.__name__
