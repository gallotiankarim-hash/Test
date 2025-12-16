from core.events import Event

class Session:
    def __init__(self):
        self.peers = []
        self.flows = []
        self.events = []
        self.findings = []

    def add_peer(self, peer):
        self.peers.append(peer)

    def add_flow(self, flow):
        self.flows.append(flow)

    def add_event(self, name, timestamp, details=None):
        self.events.append(Event(name, timestamp, details))

    def add_finding(self, finding):
        self.findings.append(finding)