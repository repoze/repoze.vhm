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

from urlparse import urlunsplit

from repoze.vhm.constants import DEFAULT_PORTS

def setServerURL(environ):
    """ Compute Zope2 'SERVER_URL' using WSGI environment.

    o Write the key into the environment.
    """
    scheme = environ.get('wsgi.url_scheme')
    if scheme is None:
        scheme = 'HTTPS' in environ and 'https' or 'http'

    http_host = environ.get('HTTP_HOST')

    # if vhm specifies a virtual host base, prefer it over the http
    # host
    vhm_host_base = environ.get('repoze.vhm.virtual_host_base')

    http_host = vhm_host_base or http_host

    if http_host:
        if ':' in http_host:
            host, port = http_host.split(':', 1)
        else:
            host = http_host
            port = None
    else:
        host = environ.get('SERVER_NAME', 'localhost')
        port = environ.get('SERVER_PORT', '8080')

    script_name = environ.get('SCRIPT_NAME', '/')

    if port is not None and port != DEFAULT_PORTS.get(scheme):
        netloc = '%s:%s' % (host, port)
    else:
        netloc = host

    url = urlunsplit((scheme, netloc, '', '', ''))
    environ['SERVER_URL'] = url
 
def getVirtualRoot(environ):
    return environ.get('repoze.vhm.virtual_root')
