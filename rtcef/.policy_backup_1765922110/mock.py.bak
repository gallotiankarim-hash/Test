from core.flow import Flow

def generate_mock_flows():
    return [
        Flow(
            src="local",
            dst="remote",
            protocol="STUN",
            metadata={"ip": "203.0.113.45", "ice_candidate": "srflx"}
        ),
        Flow(
            src="local",
            dst="relay",
            protocol="RTP",
            metadata={}
        )
    ]