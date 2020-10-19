'''
GenericDecorator 

Tidies up russian doll approach to decorators.

'''
import six
from inspect import isfunction


class DecortorMeta(type):
    def __new__(cls, name, parents, dct):
        """
        only apply decorator to non abstract models
        """

        abstract = dct.pop("abstract", None)

        cls = super(DecortorMeta, cls).__new__(cls, name, parents, dct)
        if cls.allow_bare() == False or abstract:
            return cls
        else:
            return cls()  # if no args, return an instance immediately


class GenericDecorator(six.with_metaclass(DecortorMeta)):
    """
    Tidies up russian doll approach to decorators.

    Arguments passed to the decorator at creation
    end up as self.args and self.kwargs.
    kwargs are also added to self. 
    if args_map is populated - will also add arguments pass when decorating

    args_map = ("foo",)

    @decorator("hello")

    populates self.foo with "hello"

    if there is no args_map, decorators can be used bare (without initalisation)

    e.g. @decorator

    default_kwargs sets the default value of any kwargs that might be passed in 

    default_kwargs = {"foo":"hello"}

    Override options:

    self.gateway - if it's a choice between using this function and 
    a different one

    self.arg_decorator - to adjust arguments being passed in



    """
    args_map = []
    default_kwargs = {}
    abstract = True  # disappears for children,

    def __call__(self, *args, **kwargs):
        """
        grabs the function and all arguments being passed to it
        """

        func = args[0]

        """
        if this can be used bare (but isn't) - reinit with the correct defaults
        """

        if isfunction(func) == False or kwargs:
            return self.__class__(*args, **kwargs)

        # this is a bare class that's already been used, create new child
        if self.name:
            return self.__class__()(func)

        self.function = func
        self.name = func.__name__

        def inner(*args, **kwargs):
            self.function_args = args
            self.function_kwargs = kwargs
            return self.gateway()
        inner.__name__ = self.name

        new_inner = self.post_creation(inner)

        if new_inner:
            return new_inner
        else:
            return inner

    @classmethod
    def allow_bare(cls):
        """
        can this decorator be used without initialisation?

        only if no args_map - or all values in args_map are
         already provided by default_kwargs

        """
        if cls.args_map:
            non_default = [
                x for x in cls.args_map if x not in cls.default_kwargs]
            if non_default:
                return False
            else:
                return True
        else:
            return True

    def __init__(self, *args, **kwargs):
        """
        uses the args_map and kwargs to load details in
        """
        self.args = args
        self.name = ""
        self.kwargs = {}
        if self.__class__.default_kwargs:
            self.kwargs = dict(self.__class__.default_kwargs)
        self.kwargs.update(kwargs)

        self.__dict__.update(self.kwargs)
        for x, a in enumerate(self.__class__.args_map):
            try:
                setattr(self, a, args[x])
            except IndexError:
                if a in self.kwargs:
                    continue
                else:
                    raise ValueError("Value {0} not provided".format(a))

    def gateway(self):
        """
        override if this is a "return this or something else" decorator

        return super or self.raw_decorator() to proceed
        """
        return self.raw_decorator()

    def raw_decorator(self):
        """
        accesses properties passed to decorator through self reference
        """
        obj = self.arg_decorator(
            self.function, *self.function_args, **self.function_kwargs)
        nobj = self.post_run(obj)

        # post-run may or may not return an new version of the object
        if nobj:
            return nobj
        else:
            return obj

    def arg_decorator(self, function, *args, **kwargs):
        """"
        accesses properties passed to decorated object through arguments
        """
        return function(*args, **kwargs)

    def post_run(self, obj):
        """
        passed self and the result of the function
        return final object when done
        """
        return obj

    def post_creation(self, obj):
        """
        passed self the resulting function
        return final object when done
        """
        return obj
