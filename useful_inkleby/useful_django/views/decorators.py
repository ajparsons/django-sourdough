
from django.shortcuts import  render_to_response , RequestContext


def use_template(template):
    """
    Decorator to return a HTTPResponse from a function that just returns a dictionary.
    
    Functions should return a dictionary.
    
    Usage: @use_template(template_location)
        
    """
    def outer(func):  
        def inner(request,*args,**kwargs):
            return render_to_response(template,
                                      context=func(request,*args,**kwargs),
                                      context_instance=RequestContext(request))
        return inner
    return outer
