
from django.db import models
from django.utils import timezone




class EasyBulkModel(models.Model):
    """
    Bulk Creation Mixin
    
    Mixin to help with creation of large numbers of models with streamlined syntax.
    
    """
    
    batch_time = models.DateTimeField(null=True,blank=True, editable=False)
    batch_id = models.IntegerField(null=True,blank=True, editable=False)
    __queue = list()
    
    class Meta:
        abstract = True

    @classmethod
    def _add_to_queue(cls,obj):
        """
        Add obj to class creation queue.
        """
        cls.__queue.append(obj)
        
    @classmethod  
    def save_queue(cls,safe_creation_rate = 1000, retrieve=True):
        """
        Saves all objects stored in the class queue in batches. 
        
        If retrieve = true (default) will return a list of the saved objects.
        
        """
        n = timezone.now()
        
        for x, q in enumerate(cls.__queue):
            q.batch_id = x
            q.batch_time = n
        
        def chunks(l, n):
            """Yield successive n-sized chunks from l."""
            for i in xrange(0, len(l), n):
                yield l[i:i+n]
        
        for c in chunks(cls.__queue,safe_creation_rate):
            print "saving {0} of {1}".format(len(c),cls)
            cls.objects.bulk_create(c)
        
        returning = []
        if retrieve:
            rel_q = cls.objects.filter(batch_time=n)
            lookup = {x:y for x,y in rel_q.values_list('batch_id','id')}
            
            for q in cls.__queue:
                q.id = lookup[q.batch_id]
                returning.append(q)
        
        del cls.__queue[:]
        return returning
        
    def queue(self):
        """
        Add current object to the class creation queue
        """
        self.__class__._add_to_queue(self)
        
        
        
class StockModelHelpers(object):
    """
    common functions useful for all models - diagnostics etc
    """
    def __unicode__(self):
        """
        returns the name variable is present - else the id of the object
        """
        if hasattr(self,"name"):
            return self.name
        else:
            return unicode(self.id)
        
