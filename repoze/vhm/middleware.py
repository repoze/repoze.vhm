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
from repoze.vhm.utils import getServerURL


# stolen from Paste not to add an explicit dependency
def asbool(obj):
    if isinstance(obj, (str, unicode)):
        obj = obj.strip().lower()
        if obj in ['true', 'yes', 'on', 'y', 't', '1']:
            return True
        elif obj in ['false', 'no', 'off', 'n', 'f', '0']:
            return False
        else:
            raise ValueError(
                "String is not true/false: %r" % obj)
    return bool(obj)

def munge(environ, host_header=None, root_header=None):
    """Update the environment based on a host header and/or a VHM root.
    """
    vroot_path = []
    vhosting = False

    if host_header is not None:

        vhosting = True

        (scheme, netloc, path, query, fragment) = urlsplit(host_header)
        if ':' in netloc:
            host, port = netloc.split(':')
        else:
            host = netloc
            port = DEFAULT_PORTS[scheme]
        environ['wsgi.url_scheme'] = scheme
        environ['SERVER_NAME'] = host
        environ['HTTP_HOST'] = "%s:%s" % (host, port,)
        environ['SERVER_PORT'] = port
        environ['SCRIPT_NAME'] = path
        environ['repoze.vhm.virtual_host_base'] = '%s:%s' % (host, port)

    if root_header is not None:
        vhosting = True
        environ['repoze.vhm.virtual_root'] = root_header
        vroot_path = root_header.split('/')

    if vhosting:
        server_url = getServerURL(environ)
        virtual_url_parts = [server_url]

        script_name = environ['SCRIPT_NAME']
        if script_name and script_name != '/':
            script_name_path = script_name.split('/')
            if len(script_name_path) > 1:
                virtual_url_parts += script_name_path[1:]

        real_path = environ['PATH_INFO'].split('/')
        if vroot_path:
            virtual_url_parts += real_path[len(vroot_path):]
        else:
            virtual_url_parts += real_path[1:]

        if virtual_url_parts[-1] == '':
            virtual_url_parts.pop()

        # Store the virtual URL

        environ['repoze.vhm.virtual_url'] = '/'.join(virtual_url_parts)

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
        root_header = environ.get('HTTP_X_VHM_ROOT')
        
        if root_header:
            environ['PATH_INFO'] = root_header + environ.get('PATH_INFO', '')
            
        munge(environ, host_header, root_header)
        return self.application(environ, start_response)

def make_filter(app, global_conf): #pragma NO COVER
    return VHMFilter(app)

class VHMExplicitFilter:
    """ WSGI ingress filter:

    o Converts explicitly set host and/or VHM root into "stock" CGI
      equivalents, with extra keys in the 'repoze.vhm' namespace.

    o After conversion, the environment should be suitable for munging
      via 'utils.setServerURL' (for compatibility with OFS.Traversable).

    Two configuration parameters are available, both optional.

    host -- If set, the HOST header and repoze.vhm.virtual_host_base will be
        set.
    root -- If set, repoze.vhm.virtual_root will be set.

    If either option is set, repoze.vhm.virtual_url will be calculated and
    set.
    """

    def __init__(self, application, host=None, root=None):
        self.application = application
        self.host = host
        self.root = root

    def __call__(self, environ, start_response):
        munge(environ, self.host, self.root)
        return self.application(environ, start_response)


def make_explicit_filter(app,
                         global_conf,
                         host=None,
                         root=None,
                        ): #pragma NO COVER
    return VHMExplicitFilter(app, host, root)

class VHMPathFilter:
    """ WSGI ingress filter:

    o Converts Zope2 VirtualHostMonster-style URL tokens into "stock" CGI
      equivalents, with extra keys in the 'repoze.vhm' namespace.

    o The arguement conserve_path_infos will keep the PATH_INFO variable intact
      It's pretty handy when you have a separate stock zope2 zserer
      and you want to forward the request from your WSGI pipeline

    o After conversion, the environment should be suitable for munging
      via 'setServerURL' below (for compatibility with OFS.Traversable).
    """

    def __init__(self, application, conserve_path_infos=False):
        self.application = application
        self.conserve_path_infos = conserve_path_infos

    def __call__(self, environ, start_response):

        scheme = 'HTTPS' in environ and 'https' or 'http'
        path = environ['PATH_INFO']
        vroot_path = []
        real_path = []
        script_name = ''
        script_name_path = []
        checking_vh_names = False
        vhosting = False

        elements = path.split('/')
        while elements:

            token = elements.pop(0)

            if token == 'VirtualHostBase':

                vhosting = True

                scheme = elements.pop(0)
                environ['wsgi.url_scheme'] = scheme

                host = elements.pop(0)
                if ':' in host:
                    host, port = host.split(':')
                else:
                    port = DEFAULT_PORTS[scheme]
                environ['SERVER_NAME'] = host
                environ['HTTP_HOST'] = host
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
                        script_name = '/'.join(script_name_path)
                        environ['SCRIPT_NAME'] = script_name
                    real_path.append(token)

            else:
                real_path.append(token)

        if not self.conserve_path_infos:
            environ['PATH_INFO'] = '/'.join(real_path)
            

        if vhosting:
            server_url = getServerURL(environ)
            virtual_url_parts = [server_url]

            if script_name_path:
                virtual_url_parts += script_name_path[1:]

            if vroot_path:
                virtual_url_parts += real_path[len(vroot_path):]
            else:
                virtual_url_parts += real_path[1:]

            if virtual_url_parts[-1] == '':
                virtual_url_parts.pop()

            # Store the virtual URL. Zope computes ACTUAL_URL from this,
            # for example.
            environ['repoze.vhm.virtual_url'] = '/'.join(virtual_url_parts)

        return self.application(environ, start_response)


def make_path_filter(app, global_conf, conserve_path_infos=False): #pragma NO COVER
    conserve_path_infos = asbool(conserve_path_infos)
    return VHMPathFilter(app, conserve_path_infos=conserve_path_infos)
