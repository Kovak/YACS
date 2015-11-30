def lerp(v0, v1, t):
    return (1-t)*v0 + t * v1

def lerp_color(col_1, col_2, d):
    return [lerp(c1, c2, d) for c1, c2 in zip(col_1, col_2)]
