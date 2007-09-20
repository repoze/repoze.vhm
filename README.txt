repoze.vhm README

  Overview

    This package provides some glue for doing Zope2-style virtual hosting
    within the 'repoze.zope2' environment, where the classic Zope2
    "VirtualHostMonster":http://www.zope.org/Members/4am/SiteAccess2/info
    won't work.

    It also provides CGI-environment-munging middleware that is
    potentially useful within a non-Zope WSGI application.

  Virtual Hosting in a Nutshell

    "Virtual hosting" enables dynamic applications to be served from within
    a larger URL namespace, independent of the physical location of
    the script files used to serve the application, or the precise layout of
    objects within the application.  In particular, the application and the
    server collaborate to generate URLs for links in the application, such
    that the links preserve the "apparent" location of the application.

    The simplest case requires no effort at all:  links rendered as relative
    paths from within pages work nicely.  However, such links begin to be
    problematic quickly, e.g. when the page is serving as the default index
    view for its folder, and the URL does not end in a '/'.  In that case,
    the browser interprets the links relative to the folder's parent, and
    chaos ensues.

  CGI Environment Variables

    As used for applications running "inside" Apache (e.g., using
    'mod_python'), there follwing environment variables are of interest
    when doing virtual hosting:

      'SERVER_NAME' -- the apparent hostname of the server (i.e., as
        passed in the 'Host:' header)

      'SERVER_PORT' -- the apparent port of the server

      'SCRIPT_NAME' -- any path prefix used by Apache to dispatch to
        the application (as defined via the 'ScriptAlias' directive).

      'PATH_INFO' -- the remainder of the path, after removing any parts
        used in dispatch.

  Zope2 Virtual Hosting Model

    In scenarios which use Apache rewrite + proxy to host a Zope application
    "behind" Apache, the classic Zope recipe is to rewrite the URL, adding
    virtual hosting information as extra path elements, which are then
    consumed during traversal of the Zope root by the VHM.  E.g., the
    Apache server might see a request like:

      http://www.example.com/news/politics/local/mayor_impeached.html

    And rewrite it onto the Zope backend as something like:

      http://localhost:8080/VirtualHostBase/http/www.example.com:80/cms/VirtualHostRoot/news/politics/local/mayor_impeached.html

    The VHM would then transform the request, re-converting the path into:

      /cms/news/politics/local/mayor_impeached.html

    setting the "virtual root" of the request to the '/cms' object,
    and also setting the 'SERVER_URL' in the request to:

      http://www.example.com/

  Zope3 Virtual Hosting Model

    TODO:  show the example using Z3's syntax.

  Proxy Headers Virtual Hosting Model

    This model, based on a "suggestion of Ian Bicking's",
    http://blog.ianbicking.org/2007/08/10/defaults-inheritance/ ,
    passes virtual hosting information from the proxy / web server to
    the application by adding extra headers to the proxied request:

     'HTTP_X_VHM_HOST' -- indicates the apparent URL prefix of the
        root of the application (concatenating 'wsgi.url_scheme',
        'SERVER_NAME', 'SERVER_PORT', and 'SCRIPT_NAME' variables;
        the equivalent of Zope2's 'SERVER_URL').

     'HTTP_X_VHM_ROOT' -- path of the object within the application
        which is supposed to function as the "virtual root".

    When serving an application from "within" Apache, we can just set
    the environment directly::

      <Directory /path/to/wsgiapp>
       SetEnv HTTP_X_VHM_HOST http://www.example.com/
       SetEnv HTTP_X_VHM_ROOT /cms
      </Directory>

    Proxies pass this information by adding additional headers.  E.g.,
    a sample Apache configuration for the example above might be::

      <VirtualHost *:80>
        ServerName www.example.com
        RewriteEngine on
        RewriteRule ^/(.*) http://localhost:8080/$1
        Header add X-VHm-Host http://www.example.com/
        Header add X-VHm-Root /cms
      </VirtualHost>

  'repoze.vhm' WSGI Filters

    This package provides two filters for use in the "behind" (proxied)
    scenario described above, one for each model.  When configured as
    WSGI middleware, these filters convert the path information in the
    environment from the Zope-specific syntax into the "standard" CGI
    environment variables outlined above.

  'repoze.vhm' Library API

    Because the existing Zope virtual hosting solutions do not rely
    on the "standard" CGI variables, the application dispatcher needs to
    "fix up" the environment to match Zope's expectations.  'repoze.vhm'
    offers the following functions to aid in this fixup:

      'repoze.vhm.zope2.setServerURL' -- convert the standard CGI
        virtual hosting environment into the form expected by Zope2
        (adding the 'SERVER_URL' key).

      'repoze.vhm.zope2.setVirtualRoot' -- mark the object serving
        as the virtual root for the current Zope2 request. (TODO)

