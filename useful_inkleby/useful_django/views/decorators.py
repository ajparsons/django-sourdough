'''
Created on 26 Mar 2016

@author: alex
'''

from django.shortcuts import  redirect, HttpResponseRedirect, render_to_response , RequestContext

from django.conf import settings
from django.views.decorators.cache import cache_page


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
