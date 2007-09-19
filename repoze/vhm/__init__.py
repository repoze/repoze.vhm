# repoze virtual hosting WSGI middleware

class VHM_Z3:
    def __init__(self, application):
        self.application = application
        
    def __call__(self, environ, start_response):
        # TODO: Consume VHM-style tokens from environ['PATH_INFO'] and stash
        # them away in the format expected by Zope3's vhosting.
        result = self.application(environ, start_response)
        return result
 
def make_vhm_z3(app, global_conf):
    return VHM_Z3(app)

