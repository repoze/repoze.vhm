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

from urlparse import urlsplit

from repoze.vhm.constants import DEFAULT_PORTS
portvalues = DEFAULT_PORTS.values()

class VHMFilter:
    """ WSGI ingress filter:

    o Converts HTTP header-based vhost info  into "stock" CGI
      equivalents, with extra keys in the 'repoze.vhm' namespace.

    o After conversion, the environment should be suitable for munging
      via 'utils.setServerURL' (for compatibility with OFS.Traversable).
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):

        host_header = environ.get('HTTP_X_VHM_HOST')

        if host_header is not None:
            (scheme, netloc, path, query, fragment) = urlsplit(host_header)
            if ':' in netloc:
                host, port = netloc.split(':')
            else:
                host = netloc
                port = DEFAULT_PORTS[scheme]
            environ['wsgi.url_scheme'] = scheme
            environ['SERVER_NAME'] = host
            
            if port in portvalues:
                environ['HTTP_HOST'] = host
            else:
                environ['HTTP_HOST'] = "%s:%s" % (host, port)
                
            environ['SERVER_PORT'] = port
            environ['SCRIPT_NAME'] = path
            environ['repoze.vhm.virtual_host_base'] = '%s:%s' % (host, port)

        root_header = environ.get('HTTP_X_VHM_ROOT')

        if root_header is not None:
            environ['repoze.vhm.virtual_root'] = root_header

        return self.application(environ, start_response)


def make_filter(app, global_conf):
    return VHMFilter(app)


class VHMPathFilter:
    """ WSGI ingress filter:

    o Converts Zope2 VirtualHostMonster-style URL tokens into "stock" CGI
      equivalents, with extra keys in the 'repoze.vhm' namespace.

    o After conversion, the environment should be suitable for munging
      via 'setServerURL' below (for compatibility with OFS.Traversable).
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        scheme = 'HTTPS' in environ and 'https' or 'http'
        path = environ['PATH_INFO']
        vroot_path = []
        real_path = []
        script_name_path = []
        checking_vh_names = False

        elements = path.split('/')
        while elements:

            token = elements.pop(0)

            if token == 'VirtualHostBase':

                scheme = elements.pop(0)
                environ['wsgi.url_scheme'] = scheme

                host = elements.pop(0)
                if ':' in host:
                    host, port = host.split(':')
                else:
                    port = DEFAULT_PORTS[scheme]
                environ['SERVER_NAME'] = host
                
                if port in portvalues:
                    environ['HTTP_HOST'] = host
                else:
                    environ['HTTP_HOST'] = "%s:%s" % (host, port)
                
                environ['SERVER_PORT'] = port
                environ['repoze.vhm.virtual_host_base'] = '%s:%s' \
                                                          % (host, port)

            elif token == 'VirtualHostRoot':
                vroot_path = real_path[:]  # prefix of vroot
                if vroot_path and vroot_path != ['']:
                    environ['repoze.vhm.virtual_root'] = '/'.join(vroot_path)
                else:
                    environ['repoze.vhm.virtual_root'] = '/'
                checking_vh_names = True

            elif checking_vh_names:

                if token.startswith('_vh_'): # capture external subsite
                    script_name_path.append(token[len('_vh_'):])
                else:
                    checking_vh_names = False
                    if script_name_path:
                        script_name_path.insert(0, '')
                        environ['SCRIPT_NAME'] = '/'.join(script_name_path)
                    real_path.append(token)

            else:
                real_path.append(token)

        environ['PATH_INFO'] = '/'.join(real_path)

        return self.application(environ, start_response)


def make_path_filter(app, global_conf):
    return VHMPathFilter(app)
