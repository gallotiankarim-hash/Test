def score(findings):
    score = 0
    for f in findings:
        if f["type"] == "IP_EXPOSURE":
            score += 20
        if f["type"] == "ICE_CANDIDATE":
            score += 15
    return min(score, 100)