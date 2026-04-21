def get_data(res):
    return res

def get_match(data, job):
    return data

def get_score(m):
    t = m.lower()

    score = 0

    if "python" in t:
        score += 30
    if "machine learning" in t:
        score += 30
    if "sql" in t:
        score += 20
    if "pandas" in t:
        score += 20

    return score

def get_exp(s):
    if s >= 80:
        return "good match"
    elif s >= 50:
        return "average match"
    else:
        return "low match"