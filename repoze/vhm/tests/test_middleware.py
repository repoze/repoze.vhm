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
_marker = []

class Test_munge(unittest.TestCase):
    def _callFUT(self, environ, host_header=_marker, root_header=_marker):
        from repoze.vhm.middleware import munge
        if host_header is _marker:
            if root_header is not _marker:
                return munge(environ, root_header=root_header)
            else:
                return munge(environ)
        else:
            if root_header is not _marker:
                return munge(environ, host_header, root_header)
            else:
                return munge(environ, host_header)

    def test___call___no_host_header_no_root_header_unchanged(self):
        REAL_PATH = '/a/b/c/'
        environ = {'wsgi.url_scheme': 'http',
                   'SERVER_NAME': 'example.com',
                   'SERVER_PORT': '8888',
                   'SCRIPT_NAME': '/',
                   'PATH_INFO': REAL_PATH,
                  }
        expected = environ.copy()
        self._callFUT(environ)
        self.assertEqual(environ, expected)

    def test___call___w_host_header_no_port_no_root_header(self):
        REAL_PATH = '/a/b/c/'
        environ = {'wsgi.url_scheme': 'https',
                   'SERVER_NAME': 'another.example.com',
                   'SERVER_PORT': '8888',
                   'SCRIPT_NAME': 'something',
                   'PATH_INFO': REAL_PATH,
                  }

        expected = environ.copy()
        expected['wsgi.url_scheme'] = 'http'
        expected['SERVER_NAME'] = 'example.com'
        expected['HTTP_HOST'] = 'example.com:80'
        expected['SERVER_PORT'] = '80'
        expected['SCRIPT_NAME'] = ''
        expected['repoze.vhm.virtual_host_base'] = 'example.com:80'
        expected['repoze.vhm.virtual_url'] = 'http://example.com/a/b/c'

        self._callFUT(environ, 'http://example.com')
        self.assertEqual(environ, expected)

    def test___call___w_host_header_w_port_no_root_header(self):
        REAL_PATH = '/a/b/c/'
        environ = {'wsgi.url_scheme': 'https',
                   'SERVER_NAME': 'another.example.com',
                   'SERVER_PORT': '8888',
                   'SCRIPT_NAME': 'something',
                   'PATH_INFO': REAL_PATH,
                  }

        expected = environ.copy()
        expected['wsgi.url_scheme'] = 'http'
        expected['SERVER_NAME'] = 'example.com'
        expected['HTTP_HOST'] = 'example.com:8080'
        expected['SERVER_PORT'] = '8080'
        expected['SCRIPT_NAME'] = ''
        expected['repoze.vhm.virtual_host_base'] = 'example.com:8080'
        expected['repoze.vhm.virtual_url'] = 'http://example.com:8080/a/b/c'

        self._callFUT(environ, 'http://example.com:8080')
        self.assertEqual(environ, expected)

    def test___call___no_host_header_w_root_header_no_script_name(self):
        REAL_PATH = '/a/b/c'
        environ = {'SERVER_NAME': 'example.com',
                   'SERVER_PORT': '8080',
                   'SCRIPT_NAME': '',
                   'PATH_INFO': REAL_PATH,
                  }

        expected = environ.copy()
        expected['repoze.vhm.virtual_root'] = '/a'
        expected['repoze.vhm.virtual_url'] = 'http://example.com:8080/b/c'

        self._callFUT(environ, root_header='/a')
        self.assertEqual(environ, expected)

    def test___call___no_host_header_w_root_header_trailing_slash(self):
        REAL_PATH = '/a/b/c/'
        environ = {'SERVER_NAME': 'example.com',
                   'SERVER_PORT': '8080',
                   'SCRIPT_NAME': '',
                   'PATH_INFO': REAL_PATH,
                  }

        expected = environ.copy()
        expected['repoze.vhm.virtual_root'] = '/a'
        expected['repoze.vhm.virtual_url'] = 'http://example.com:8080/b/c'

        self._callFUT(environ, root_header='/a')
        self.assertEqual(environ, expected)

    def test___call___no_host_header_w_root_header_w_script_name_short(self):
        REAL_PATH = '/a/b/c'
        environ = {'SERVER_NAME': 'example.com',
                   'SERVER_PORT': '8080',
                   'SCRIPT_NAME': 'foo',
                   'PATH_INFO': REAL_PATH,
                  }

        expected = environ.copy()
        expected['repoze.vhm.virtual_root'] = '/a'
        expected['repoze.vhm.virtual_url'] = 'http://example.com:8080/b/c'

        self._callFUT(environ, root_header='/a')
        self.assertEqual(environ, expected)

    def test___call___no_host_header_w_root_header_w_script_name_longer(self):
        REAL_PATH = '/a/b/c'
        environ = {'SERVER_NAME': 'example.com',
                   'SERVER_PORT': '8080',
                   'SCRIPT_NAME': 'foo/bar',
                   'PATH_INFO': REAL_PATH,
                  }

        expected = environ.copy()
        expected['repoze.vhm.virtual_root'] = '/a'
        expected['repoze.vhm.virtual_url'] = 'http://example.com:8080/bar/b/c'

        self._callFUT(environ, root_header='/a')
        self.assertEqual(environ, expected)

class MungeReplacer:

    _old_munge = None

    def tearDown(self):
        if self._old_munge is not None:
            self._set_munge(self._old_munge)

    def _set_munge(self, func):
        from repoze.vhm import middleware
        middleware.munge, self._old_munge = func, middleware.munge

    def _get_munged(self):
        _munged = {}
        def _munge(environ, host_header, root_header):
            _munged['host_header'] = host_header
            _munged['root_header'] = root_header
        self._set_munge(_munge)
        return _munged

class TestXHeaders(MungeReplacer, unittest.TestCase):
    # Test that VHMFilter calls munge apprpriately

    def _getTargetClass(self):
        from repoze.vhm.middleware import VHMFilter
        return VHMFilter

    def _makeOne(self, app):
        return self._getTargetClass()(app)

    def test___call___no_markers(self):
        # Environments which do not have markers don't get munged.
        _munged = self._get_munged()
        expected = {}
        app = VHMTestApp(expected)
        filter = self._makeOne(app)
        environ = {}

        filter(environ, noopStartResponse)

        self.assertEqual(_munged['host_header'], None)
        self.assertEqual(_munged['root_header'], None)

    def test___call___X_VHM_HOST(self):
        _munged = self._get_munged()
        expected = {}
        app = VHMTestApp(expected)
        filter = self._makeOne(app)
        X_VHM_HOST = 'http://example.com:80/script'
        environ = {'HTTP_X_VHM_HOST': X_VHM_HOST}

        filter(environ, noopStartResponse)

        self.assertEqual(_munged['host_header'], X_VHM_HOST)
        self.assertEqual(_munged['root_header'], None)

    def test___call___X_VHM_ROOT(self):
        _munged = self._get_munged()
        expected = {}
        app = VHMTestApp(expected)
        filter = self._makeOne(app)
        X_VHM_ROOT = '/a/b'
        environ = {'HTTP_X_VHM_ROOT': X_VHM_ROOT}

        filter(environ, noopStartResponse)

        self.assertEqual(_munged['host_header'], None)
        self.assertEqual(_munged['root_header'], X_VHM_ROOT)

    def test___call___X_VHM_HOST_and_X_VHM_ROOT(self):
        _munged = self._get_munged()
        expected = {}
        app = VHMTestApp(expected)
        filter = self._makeOne(app)
        X_VHM_HOST = 'http://example.com:80/script'
        X_VHM_ROOT = '/a/b'
        environ = {'HTTP_X_VHM_HOST': X_VHM_HOST,
                   'HTTP_X_VHM_ROOT': X_VHM_ROOT,
                  }

        filter(environ, noopStartResponse)

        self.assertEqual(_munged['host_header'], X_VHM_HOST)
        self.assertEqual(_munged['root_header'], X_VHM_ROOT)
        
    def test___call___X_VHM_HOST_and_X_VHM_ROOT_correctly_sets_PATH_INFO(self):
        """
        When getting a request at ``http://example.com:80/c/d/e/f``, the 
        PATH_INFO needs to be set to account for the actual zope root
        """
        _munged = self._get_munged()
        expected = {}
        app = VHMTestApp(expected)
        filter = self._makeOne(app)
        X_VHM_HOST = 'http://example.com:80/'
        X_VHM_ROOT = '/a/b'
        environ = {'HTTP_X_VHM_HOST': X_VHM_HOST,
                   'HTTP_X_VHM_ROOT': X_VHM_ROOT,
                   'PATH_INFO' : '/c/d/e/f'
                  }

        filter(environ, noopStartResponse)

        self.assertEqual(environ['PATH_INFO'], '/a/b/c/d/e/f')
        
    def test___call___X_VHM_HOST_only_does_not_set_PATH_INFO(self):
        _munged = self._get_munged()
        expected = {}
        app = VHMTestApp(expected)
        filter = self._makeOne(app)
        X_VHM_HOST = 'http://example.com:80/'
        environ = {'HTTP_X_VHM_HOST': X_VHM_HOST,
                   'PATH_INFO': '/a/b/c'
                  }

        filter(environ, noopStartResponse)

        self.assertEqual(environ['PATH_INFO'], '/a/b/c')
        

class TestExplicit(MungeReplacer, unittest.TestCase):

    def _getTargetClass(self):
        from repoze.vhm.middleware import VHMExplicitFilter
        return VHMExplicitFilter

    def _makeOne(self, app, host=None, root=None):
        return self._getTargetClass()(app, host, root)

    def test___call___no_host_no_root(self):
        _munged = self._get_munged()
        expected = {}
        app = VHMTestApp(expected)
        filter = self._makeOne(app)
        environ = {}

        filter(environ, noopStartResponse)

        self.assertEqual(_munged['host_header'], None)
        self.assertEqual(_munged['root_header'], None)

    def test___call___w_host_no_root(self):
        _munged = self._get_munged()
        expected = {}
        app = VHMTestApp(expected)
        X_VHM_HOST = 'http://example.com:80/script'
        filter = self._makeOne(app, host=X_VHM_HOST)
        environ = {}

        filter(environ, noopStartResponse)

        self.assertEqual(_munged['host_header'], X_VHM_HOST)
        self.assertEqual(_munged['root_header'], None)

    def test___call___no_host_w_root(self):
        _munged = self._get_munged()
        expected = {}
        app = VHMTestApp(expected)
        X_VHM_ROOT = '/a/b'
        filter = self._makeOne(app, root=X_VHM_ROOT)
        environ = {}

        filter(environ, noopStartResponse)

        self.assertEqual(_munged['host_header'], None)
        self.assertEqual(_munged['root_header'], X_VHM_ROOT)

    def test___call___w_host_w_root(self):
        _munged = self._get_munged()
        expected = {}
        app = VHMTestApp(expected)
        X_VHM_HOST = 'http://example.com:80/script'
        X_VHM_ROOT = '/a/b'
        filter = self._makeOne(app, X_VHM_HOST, X_VHM_ROOT)
        environ = {}

        filter(environ, noopStartResponse)

        self.assertEqual(_munged['host_header'], X_VHM_HOST)
        self.assertEqual(_munged['root_header'], X_VHM_ROOT)


class TestVHMPathFilter(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.vhm.middleware import VHMPathFilter
        return VHMPathFilter

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
        self.assertEqual(expected.get('repoze.vhm.virtual_url'), None)
        self.assertEqual(expected.get('repoze.vhm.virtual_root'), None)
        self.assertEqual(expected.get('repoze.vhm.virtual_host_base'), None)

    def test___call___VirtualHostBase_no_port(self):
        # VHB: consume next two tokens, converts to new scheme / netloc.
        #      Note we preserve the port here (elided by 'setServerURL').
        expected = {}
        app = VHMTestApp(expected)
        filter = self._makeOne(app)
        PREFIX = '/VirtualHostBase/http/example.com'
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
        self.assertEqual(expected['repoze.vhm.virtual_url'],
                                  'http://example.com/a/b/c')
        self.assertEqual(expected.get('repoze.vhm.virtual_root'), None)
        self.assertEqual(expected['repoze.vhm.virtual_host_base'],
                         'example.com:80')

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
        self.assertEqual(expected['repoze.vhm.virtual_url'],
                                  'http://example.com/a/b/c')
        self.assertEqual(expected.get('repoze.vhm.virtual_root'), None)
        self.assertEqual(expected['repoze.vhm.virtual_host_base'],
                         'example.com:80')

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
        self.assertEqual(expected['repoze.vhm.virtual_url'],
                                  'http://example.com:8000/a/b/c')
        self.assertEqual(expected.get('repoze.vhm.virtual_root'), None)
        self.assertEqual(expected['repoze.vhm.virtual_host_base'],
                         'example.com:8000')

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
        self.assertEqual(expected['repoze.vhm.virtual_url'],
                                  'https://example.com/a/b/c')
        self.assertEqual(expected.get('repoze.vhm.virtual_root'), '/')
        self.assertEqual(expected['repoze.vhm.virtual_host_base'],
                         'example.com:443')

    def test___call___VirtualHostRoot_conservativepathinfos(self):
        # VHR immediately following VHB + 2 -> no vroot.
        expected = {}
        app = VHMTestApp(expected)
        filter = self._makeOne(app)
        filter.conserve_path_infos = True
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
        self.assertEqual(expected['PATH_INFO'], '/VirtualHostBase/http/example.com:80'
                         '/VirtualHostRoot/_vh_sub1/_vh_sub2/a/b/c/')
        self.assertEqual(expected['repoze.vhm.virtual_url'],
                                  'http://example.com/sub1/sub2/a/b/c')
        self.assertEqual(expected.get('repoze.vhm.virtual_root'), '/')
        self.assertEqual(expected['repoze.vhm.virtual_host_base'],
                         'example.com:80')  
 
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
        self.assertEqual(expected['repoze.vhm.virtual_url'],
                                  'http://example.com/a/b/c')
        self.assertEqual(expected.get('repoze.vhm.virtual_root'), '/sub1')
        self.assertEqual(expected['repoze.vhm.virtual_host_base'],
                         'example.com:80')

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
        self.assertEqual(expected['repoze.vhm.virtual_url'],
                                  'http://example.com/sub1/sub2/a/b/c')
        self.assertEqual(expected.get('repoze.vhm.virtual_root'), '/')
        self.assertEqual(expected['repoze.vhm.virtual_host_base'],
                         'example.com:80')

def noopStartResponse(status, headers):
    pass

class VHMTestApp:
    def __init__(self, _called_environ):
        self._called_environ = _called_environ

    def __call__(self, environ, start_response):
        self._called_environ.clear()
        self._called_environ.update(environ)
        return self.__class__.__name__

