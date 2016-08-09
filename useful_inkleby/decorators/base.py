'''
Created on Jul 25, 2016

@author: Alex
'''

class GenericDecorator(object):
    """
    tidies up shellgame of decorators. 
    arguments passed to the decorator at creation
    end up as self.args and self.kwargs.
    kwargs are also added to self. 
    if args_map is populated - will also add those to self
    
    args_map = ("foo",)
    
    populates self.foo with args[0]
    
    override self.gateway if it's a choice between using this function and a different one
    
    overide self.arg_decorator to adjust arguments being passed in
    
    expects self, function, then delivers any args and kwargs passed to the function
    
    """
    args_map = []
    
    def __call__(self,func):
        """
        grabs the function and all arguments being passed to it
        """
        self.function = func
        
        def inner(*args,**kwargs):
            self.function_args = args
            self.function_kwargs = kwargs
            return self.gateway()
        
        return inner
    
    def __init__(self,*args,**kwargs):
        """
        uses the args_map and kwargs to load details in
        """
        self.args = args
        self.kwargs = kwargs
        
        self.__dict__.update(kwargs)
        for x,a in enumerate(self.__class__.args_map):
            setattr(self,a,args[x])
            
    def gateway(self):
        """
        override if this is a "return this or something else
        
        Use super or call self.raw_decorator() to proceed
        """
        return self.raw_decorator()
            
    def raw_decorator(self):
        """
        accesses properties passed to decorated through self reference
        """
        return self.arg_decorator(self.function,*self.function_args,**self.function_kwargs)
    
    def arg_decorator(self,function,*args,**kwargs):
        """"
        accesses properties passed to decorated object through arguments
        """
        return function(*args,**kwargs)
    
 
