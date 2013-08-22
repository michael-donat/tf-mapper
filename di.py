__author__ = 'thornag'

class ComponentContainer:
    def __init__(self):
        self.components = {}
    def __getitem__(self, component):
        try:
            componentClass = self.components[component]
        except KeyError:
            raise KeyError, "Unknown component named %r" % component
        return componentClass()
    def register(self, component, componentClass, *args, **kwargs):
        if callable(componentClass):
            def componentInstance(): return componentClass(*args, **kwargs)
        else:
            def componentInstance(): return componentClass

        self.components[component] = componentInstance

container = ComponentContainer()

class ComponentRequest(object):
    def __init__(self, component):
        self.component = component
    def __get__(self, obj, T):
        return self.result # <-- will request the feature upon first call
    def __getattr__(self, name):
        self.result = container[self.component]
        return self.result
