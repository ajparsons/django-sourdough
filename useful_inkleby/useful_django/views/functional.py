'''
Created on 26 Mar 2016

@author: alex
'''


from django.shortcuts import render, RequestContext
from django.http.response import HttpResponse

class FunctionalView(object):
    """
    Very simple class-based view that simple expects the class to have a 
    'template' variable and a 'view' function that expects (self, request). 
    
    
    Idea is to preserve cleanness of functional view logic but tidy up the 
    most common operation. 
    
    """
    
    
    template = ""
    require_staff = False
    view_decorators = []
    
    @classmethod
    def as_view(cls):
        """
        inner func hides that we need to pass a self arg to the view
        """
        
        def render_func(request,*args,**kwargs):
            
            if cls.require_staff and request.user.is_staff == False:
                return HttpResponse("No Access")
            
            view = cls()
            
            context = view.view(request,*args,**kwargs)
            
            if isinstance(context,dict):
                context = view.extra_params(context)
                return view.context_to_html(request,context)
            else:
                #if we're returning a redirect view
                return context
        
        func = render_func
        
        for v in cls.view_decorators:
            func = v(func)
        
        return func

    def extra_params(self,context):
        return context

    def context_to_html(self,request,context):
        html = render(request,
                      self.__class__.template,
                      context=context,
                      context_instance=RequestContext(request)
                      )
        return html
    

    def view(self,request):
        """
        dummy view - should almost always be subclassed out 
        (unless idea is to use raw template).
        should return a dictionary with context to be fed to template. 
        """
        return {}
    
    