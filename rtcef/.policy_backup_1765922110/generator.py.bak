def generate_report(session, score):
    return {
        "summary": f"{len(session.findings)} exposures detected",
        "score": score,
        "findings": session.findings,
        "events": [e.name for e in session.events]
    }