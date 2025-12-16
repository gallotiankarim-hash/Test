class ExposureEngine:
    def analyze(self, flow):
        findings = []

        if "ip" in flow.metadata:
            findings.append({
                "type": "IP_EXPOSURE",
                "value": flow.metadata["ip"],
                "protocol": flow.protocol,
                "direction": "outbound"
            })

        if "ice_candidate" in flow.metadata:
            findings.append({
                "type": "ICE_CANDIDATE",
                "value": flow.metadata["ice_candidate"]
            })

        return findings