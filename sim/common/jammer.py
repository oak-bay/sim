from .. import Entity


class Jammer(Entity):
    """ 干扰机. """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.power_on = False
        self.kind = kwargs['kind'] if 'kind' in kwargs else 'jam'
