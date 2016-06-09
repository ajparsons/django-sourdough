from django.db import models
from django.db.models.base import ModelBase
from ..models import ApplyManagerMethodMeta
import json
import six

try:
    import cpickle as pickle
except ImportError:
    import pickle


class BasicSerial(object):
    
    """
    very basic recursive object serialiser
    """
    
    allowed = [str, unicode, int, float]
    classes = {}

    @classmethod
    def loads(cls,obj):
        di = json.loads(obj)
        return cls.restore_object(di)
    
     
    @classmethod   
    def dumps(cls,obj):
        di = cls.convert_object(obj)
        return json.dumps(di)

    @classmethod
    def convert_object(cls, obj):
        """
        convert all objects to dictionaries - otherwise preserve structure
        """
        
        if obj == None:
            return obj
        
        for a in cls.allowed:
            if isinstance(obj, a):
                return obj

        if isinstance(obj, list):
            return [cls.convert_object(x) for x in obj]

        if isinstance(obj, dict):
            return {x: cls.convert_object(y) for x, y in obj.iteritems()}

        # all other objects
        """
        if registered, store using a basic recursive dictionary approach (easier to edit)
        """
        if obj.__class__.__name__ in cls.classes: 
            return obj.serial_dumps()
        else: #otherwise just do a normal pickle
            return {"_type": obj.__class__.__name__,
                    "_pickle": pickle.dumps(obj)}

    @classmethod
    def restore_object(cls, obj):
        """
        recreate objects bases on classes currently avaliable
        """

        if obj == None:
            return obj

        for a in cls.allowed:
            if isinstance(obj, a):
                return obj

        if isinstance(obj, list):
            return [cls.restore_object(x) for x in obj]

        if isinstance(obj, dict):
            
            if "_type" in obj:
                t = obj["_type"]
                
                #restored registered classes
                if t in cls.classes and "_content" in obj:
                    model = cls.classes[t]
                    return model.serial_loads(obj)
            
            
            #restored pickled classes
            if "_pickle" in obj:
                # object restoration

                ins = pickle.loads(str(obj["_pickle"]))
                
                return ins
            else:
                #recursive dictionary restore
                return {x: cls.restore_object(y) for x, y in obj.iteritems()}

def register_for_serial(cls):
    """
    decorator that registers a class so it can be converted 
    into a json block
    
    -if a class isn't registered it will 
    
    """
    BasicSerial.classes[cls.__name__] = cls
    return cls

class SerialMeta(type):
    """
    customise the metaclass to apply the serial registration decorator
    """
    def __new__(cls, name, parents, dct):
        
        """
        only apply decorator to non abstract models
        """
        cls = super(SerialMeta, cls).__new__(cls, name, parents, dct)

        return register_for_serial(cls)
 
class SerialMetaModel(ApplyManagerMethodMeta):
    """
    customise the metaclass to apply the serial registration decorator to models
    """
    def __new__(cls, name, parents, dct):
        
        """
        only apply decorator to non abstract models
        """
    
        cls = super(SerialMetaModel, cls).__new__(cls, name, parents, dct)

        return register_for_serial(cls)
 
class SerialBase(object):
    """
    All classes are automatically registered with the serialising function.
    """
    
    @classmethod
    def serial_loads(cls, obj):
        ins = cls.__new__(cls)
        ins.__dict__.update({x: BasicSerial.restore_object(y)
                             for x, y in obj["_content"].iteritems()})
        return ins

    def serial_dumps(self):
        return {"_type": self.__class__.__name__,
                "_content": BasicSerial.convert_object(self.__dict__)}   

 
class SerialObject(six.with_metaclass(SerialMeta, SerialBase)):
    pass

class SerialModel(six.with_metaclass(SerialMetaModel,models.Model,SerialBase)):
    pass

    class Meta:
        abstract = True
 


class JsonBlockField(models.TextField):
    """
    store a collection of generic objects in a jsonblock. 
    Useful for when you have a hierarchy of classes that are only accessed
    from the one object. 
    """

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return []
        return BasicSerial.loads(value)

    def to_python(self, value):
        if isinstance(value, list):
            return value

        if value is None:
            return value

        return BasicSerial.loads(value)

    def get_prep_value(self, value):
        return BasicSerial.dumps(value)
