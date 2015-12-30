import copy

__author__ = 'matt'


class CoyoteEntityAbstract(object):

    def clone(self):
        cloned = copy.deepcopy(self)
        return cloned

    def clone_and_update(self, **kwargs):
        """Clones the object and updates the clone with the args

        @param kwargs: Keyword arguments to set
        @return: The cloned copy with updated values
        """
        cloned = self.clone()
        cloned.update(**kwargs)
        return cloned

    def update(self, **kwargs):
        """Sets that specified args to the objects attributes

        @param kwargs: Keyword arguments to set the class
        @return: None
        """
        for k, v in kwargs.iteritems():
            if hasattr(self, k):
                setattr(self, k, v)