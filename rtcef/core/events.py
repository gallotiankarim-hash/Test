class Event:
    def __init__(self, name, timestamp, details=None):
        self.name = name
        self.timestamp = timestamp
        self.details = details or {}