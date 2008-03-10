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
            environ['SERVER_PORT'] = port
            environ['SCRIPT_NAME'] = path
            environ['repoze.vhm.virtual_host_base'] = '%s:%s' % (host, port)

        root_header = environ.get('HTTP_X_VHM_ROOT')

        if root_header is not None:
            environ['repoze.vhm.virtual_root'] = root_header
 
        return self.application(environ, start_response)
 
def make_filter(app, global_conf):
    return VHMFilter(app)
