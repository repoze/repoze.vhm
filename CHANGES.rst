repoze.vhm Changelog
====================

0.16 (unreleased)
-----------------

- Nothing changed yet.


0.15 (2020-06-19)
-----------------

- Add support for testing on Travis.

- Drop support for Python 2.6.

- Add support fo Python 3.4, 3.5, and 3.6.

0.14 (2012-03-24)
-----------------

- Ensure HTTP_HOST is set correctly for non-standard ports under VHM paths.
  This header requires a trailing port if not the default for a given service.
  See http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.23.
  [davidjb]

0.13 (2010-04-18)
-----------------

- add conserve_path_infos for the VHMPathFilter middleware [kiorky]

0.12 (2010-01-01)
-----------------

- Update tests of middleware to check only that ``munge`` is called correctly.

- Test ``munge`` sepearately.

- 100% test coverage.

- fixed xheaders filter to set PATH_INFO correctly
  [vangheem]
  

0.11 (2009-08-31)
-----------------

- Add a repoze.vhm#vhm_explicit filter. This is like the vhm_xheaders
  middleware, but the VHM host and/or root are set in the WSGI configuration
  instead of in the request.

- Calculate a VIRTUAL_URL and put it into the environment. This is basically
  the URL that the end user sees. repoze.zope2 >= 1.0.2 uses this to compute
  the ACTUAL_URL request variable, for example.

0.10 (2009-08-26)
-----------------

- Apply the HTTP_HOST port number fix to the VHM Path filter as well.

0.9 (2009-07-09)
----------------

- 100% test coverage.

- ``HTTP_HOST`` parameter now includes port number if not http:80 or
  https:443.  Thanks to Martin Aspeli.

0.8 (2009-01-10)
----------------

- Set 'HTTP_HOST' in environ to the same value as 'SERVER_NAME', FBO apps
  which need it.

0.7 (2008-05-07)
----------------

- Remove 'dependency-links=' to dist.repoze.org to prevent easy_install
  from searching there inappropriately.

0.6 (2008-04-17)
----------------

- Re-added the path-segment-based filter as an option, to support scenarios
  in which the reverse proxy can be configured to rewrite the URL but not
  to add headers.

0.5 (2008-03-09)
----------------

- Brown bag release: I fudged the entry point for the xheaders filter.

0.4 (2008-03-09)
----------------

- Kill off path-segment-based filter (repoze.vhm.zope2).  Only the
  xheaders filter remains.

- Add license headers.

- The middleware now sets a 'repoze.vhm.virtual_host_base' which is
  preferred by setServerUrl over 'HTTP_HOST' when present.

- Add a getVirtualRoot API.

0.3 (2007-10-25)
----------------

- Fix setServerURL method to take into account HTTP_HOST passed by
  client.

0.2 (2007-09-22)
----------------

- Change repoze.vhm.zope2:setServerURL to allow Zope 2 to generate the
  correct request['URL'] value when the vhm is in the pipeline.

0.1 (2007-09-21)
----------------

- Initial release.
