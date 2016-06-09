'''
Created on 26 Mar 2016

@author: alex
'''

from django.shortcuts import render_to_response, RequestContext


def use_template(template):
    """
    decorator to return a HTTPResponse from a function that just returns a dictionary
    
    @use_template("blah.html")
    def foo (request):
        return {"bar":True}
        
    """
    def outer(func):  
        def inner(request,*args,**kwargs):
            return render_to_response(template,
                                      context=func(request,*args,**kwargs),
                                      context_instance=RequestContext(request))
        return inner
    return outer
