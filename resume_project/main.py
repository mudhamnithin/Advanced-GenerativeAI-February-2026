from chains.flow import get_data, get_match, get_score, get_exp

job = "python machine learning sql pandas"

r1 = "python machine learning sql pandas"
r2 = "python machine learning"
r3 = "html css"

def run(res):
    print("\nrun start\n")

    d = get_data(res)
    print("data:", d)

    m = get_match(d, job)
    print("match:", m)

    s = get_score(m)
    print("score:", s)

    e = get_exp(s)
    print("exp:", e)

run(r1)
run(r2)
run(r3)