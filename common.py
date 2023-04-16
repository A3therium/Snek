def clamp(num,floor,roof):
    return max(floor, min(num,roof))

def arrAdd(a, b) -> list:
    res = []
    for i in range(0,len(a)):
        res.append(a[i] + b[i])
    return res