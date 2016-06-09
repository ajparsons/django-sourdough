'''

FlexiModel tidies up adding up methods to models and querysets.

Usage:

from useful_django.models.flexi import FlexiModel, querysetmethod, managermethod

class Foo(FlexiModel):
    
    @querysetmethod
    def bar():
        pass
        
    @managermethod
    def foobar():
        pass
    
Foo.objects.foobar()
Foo.objects.all().bar()


'''

import six
from django.db import models
from django.db.models.base import ModelBase

def allow_floating_methods(cls):
    """
    decorator for models that allows functions to be transposed to querysets and managers
    can decorate models directly - or make a subclass of FlexiModel.
    
    """
    class CustomQuerySet(models.QuerySet):
        pass
     
    """
    move flagged queryset methods to queryset
    """
    for i in cls.__dict__.keys():
        method = cls.__dict__[i]
        if hasattr(method,"_querysetmethod"):
            setattr(CustomQuerySet,i,method)    
     
    class CustomManager(models.Manager):
        use_for_related_fields = True
         
        def get_queryset(self):
            return CustomQuerySet(self.model, using=self._db)        

    """
    move flagged manager methods to manager
    """     
    for i in cls.__dict__.keys():
        method = cls.__dict__[i]
        if hasattr(method,"_managermethod"):
            setattr(CustomManager,i,method)
             
    cls._default_manager = CustomManager
    cls.add_to_class('objects',CustomManager())
    return cls
     
class ApplyManagerMethodMeta(ModelBase):
    """
    customise the metaclass to apply a decorator that allows custom manager
    and queryset methods
    """
    def __new__(cls, name, parents, dct):
        
        """
        only apply decorator to non abstract models
        """
        is_abstract = False
        try:
            if dct['Meta'].abstract:
                is_abstract = True
        except KeyError:
            pass
             
        cls = super(ApplyManagerMethodMeta, cls).__new__(cls, name, parents, dct)
        if is_abstract:
            return cls
        else:
            return allow_floating_methods(cls)
 
class FlexiModel(six.with_metaclass(ApplyManagerMethodMeta,models.Model)):
    """
    class for models to inherit to receive correct metaclass that allows the floating decorators
    
    use instead of models.Model
    """
     
    class Meta:
        abstract = True
 
def querysetmethod(func):
    """
    decorator for a model method to make it apply to the queryset.
     
    @querysetmethod
    def foo(self):
        pass
        
    will be accessible as model.objects.all().foo()
     
    "self" will then be the query object.
     
    """
    func._querysetmethod = True
    return func  
 
def managermethod(func):
    """
    decorator for a model method to make it a manager method instead.
    
    @managermethod
    def foo(self):
        pass
        
    will be accessible as model.objects.foo()
     
    "self" will then be the manager object.
    
    self.model - can then be used to access model.
    self.get_queryset() - to get access to a query
    
    """
    
    func._managermethod = True
    return func