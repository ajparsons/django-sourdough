'''
Created on 26 Mar 2016

@author: alex
'''


from django.shortcuts import render, RequestContext

class FunctionalView(object):
    """
    Very simple class-based view that simple expects the class to have a 
    'template' variable and a 'view' function that expects (self, request). 
    
    
    Idea is to preserve cleanness of functional view logic but tidy up the 
    most common operation. 
    
    """
    
    
    template = ""
    
    @classmethod
    def as_view(cls):
        """
        inner func hides that we need to pass a self arg to the view
        """
        
        def render_func(request,*args,**kwargs):
            context = cls().view(request,*args,**kwargs)
            return cls().context_to_html(request,context)
            
        return render_func

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
    
    