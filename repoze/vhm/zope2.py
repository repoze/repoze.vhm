from urlparse import urlunsplit

from repoze.vhm.constants import DEFAULT_PORTS

class VHMFilter:
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
                    environ['SERVER_NAME'] = host
                    environ['SERVER_PORT'] = port
                else:
                    environ['SERVER_NAME'] = host

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

def setServerURL(environ):
    """ Compute Zope2 'SERVER_URL' using WSGI environment.

    o Write the key into the environment.
    """
    scheme = environ.get('wsgi.url_scheme')
    if scheme is None:
        scheme = 'HTTPS' in environ and 'https' or 'http'

    http_host = environ.get('HTTP_HOST')
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
 
def make_filter(app, global_conf):
    return VHMFilter(app)
