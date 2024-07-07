
event_names=('DISPLAY_PDF_FILE',)

class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class EventDispatcher(metaclass=SingletonMeta):
    def __init__(self):
        self.listeners = {}

    def register_listener(self, event_name : str, callback):
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(callback)

    def dispatch_event(self, event_name, data):
        if event_name in self.listeners:
            for callback in self.listeners[event_name]:
                callback(data)