# exceptions.py
#
# Authors:
#   - Coumes Quentin <coumes.quentin@gmail.com>


import requests



def status_exceptions(response: requests.Response):
    """Returns the Exception corresponding to <response>'s status code."""
    return globals()["Sandbox" + str(response.status_code)](response)



class SandboxError(Exception):
    """Base Exception for sandbox_api."""
    
    
    def __init__(self, response: requests.Response, message: str = None):
        self.message = message
        self.response = response
    
    
    def __str__(self):
        return ("Sandbox '%s' responded with status %d - %s"
                % (self.response.url, self.response.status_code, self.response.content))



class Sandbox300(SandboxError):
    pass



class Sandbox301(SandboxError):
    pass



class Sandbox302(SandboxError):
    pass



class Sandbox303(SandboxError):
    pass



class Sandbox304(SandboxError):
    pass



class Sandbox305(SandboxError):
    pass



class Sandbox307(SandboxError):
    pass



class Sandbox308(SandboxError):
    pass



class Sandbox400(SandboxError):
    pass



class Sandbox401(SandboxError):
    pass



class Sandbox402(SandboxError):
    pass



class Sandbox403(SandboxError):
    pass



class Sandbox404(SandboxError):
    pass



class Sandbox405(SandboxError):
    pass



class Sandbox406(SandboxError):
    pass



class Sandbox407(SandboxError):
    pass



class Sandbox408(SandboxError):
    pass



class Sandbox409(SandboxError):
    pass



class Sandbox410(SandboxError):
    pass



class Sandbox411(SandboxError):
    pass



class Sandbox412(SandboxError):
    pass



class Sandbox413(SandboxError):
    pass



class Sandbox414(SandboxError):
    pass



class Sandbox415(SandboxError):
    pass



class Sandbox416(SandboxError):
    pass



class Sandbox417(SandboxError):
    pass



class Sandbox421(SandboxError):
    pass



class Sandbox422(SandboxError):
    pass



class Sandbox423(SandboxError):
    pass



class Sandbox424(SandboxError):
    pass



class Sandbox426(SandboxError):
    pass



class Sandbox428(SandboxError):
    pass



class Sandbox429(SandboxError):
    pass



class Sandbox431(SandboxError):
    pass



class Sandbox451(SandboxError):
    pass



class Sandbox500(SandboxError):
    pass



class Sandbox501(SandboxError):
    pass



class Sandbox502(SandboxError):
    pass



class Sandbox503(SandboxError):
    pass



class Sandbox504(SandboxError):
    pass



class Sandbox505(SandboxError):
    pass



class Sandbox506(SandboxError):
    pass



class Sandbox507(SandboxError):
    pass



class Sandbox508(SandboxError):
    pass



class Sandbox510(SandboxError):
    pass



class Sandbox511(SandboxError):
    pass
