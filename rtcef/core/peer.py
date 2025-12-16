class Peer:
    def __init__(self, role, identifier=None):
        self.role = role  # local | remote | relay
        self.identifier = identifier
        self.exposures = []

    def add_exposure(self, exposure):
        self.exposures.append(exposure)