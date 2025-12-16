class Flow:
    def __init__(self, src, dst, protocol, metadata=None):
        self.src = src
        self.dst = dst
        self.protocol = protocol
        self.metadata = metadata or {}