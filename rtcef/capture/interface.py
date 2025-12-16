class CaptureInterface:
    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def get_flows(self):
        return []