from math import pi, cos, sin

def draw_offset_layered_regular_polygon(pos, levels, sides, 
    middle_color, radius_color_dict):
    '''
    radius_color_dict = {'level#': (even_r, odd_r), (r,g,b,a))}
    '''
    x, y = pos
    angle = 2 * pi / sides
    all_verts = {}
    all_verts[0] = {'pos': pos, 'v_color': middle_color}
    r_total_e = 0
    r_total_o = 0
    i = 0
    indices = []
    vert_count = 1
    ind_count = 0
    ind_ext = indices.extend
    for count in range(levels):
        level = i + 1
        rs, color = radius_color_dict[level]
        even_r, odd_r = rs
        for s in range(sides):
            r = odd_r if not s % 2 else even_r
            r_total = r_total_o if not s % 2 else r_total_e
            new_pos = list((x + (r + r_total) * sin(s * angle), 
                y + (r + r_total) * cos(s * angle)))
            all_verts[vert_count] = {'pos': new_pos, 'v_color': color}
            vert_count += 1
        r_total_e += even_r
        r_total_o += odd_r
        c = 1 #side number we are on in loop
        if level == 1:
            for each in range(sides):
                if c < sides:
                    ind_ext((c, 0, c+1))
                else:
                    ind_ext((c, 0, 1))
                ind_count += 3
                c += 1
        else:
            for each in range(sides):
                offset = sides*(i-1)
                if c < sides:
                    ind_ext((c+sides+offset, c+sides+1+offset, c+offset))
                    ind_ext((c+offset, c+1+offset, c+sides+1+offset))
                else:
                    ind_ext((c+sides+offset, sides+1+offset, sides+offset))
                    ind_ext((sides+offset, 1+offset, sides+1+offset))
                ind_count += 6
                c += 1
        i += 1
    return {'indices': indices, 'vertices': all_verts, 
        'vert_count': vert_count, 'ind_count': ind_count}

def draw_layered_regular_polygon(pos, levels, sides, middle_color,
    radius_color_dict):
    '''
    radius_color_dict = {level#: (r, (r,g,b,a))}
    '''
    x, y = pos
    angle = 2 * pi / sides
    all_verts = {}
    all_verts[0] = {'pos': pos, 'v_color': middle_color}
    r_total = 0
    i = 0
    indices = []
    vert_count = 1
    ind_count = 0
    ind_ext = indices.extend 
    for count in range(levels):
        level = i + 1
        r, color = radius_color_dict[level]
        for s in range(sides):
            new_pos = list((x + (r + r_total) * sin(s * angle), 
                y + (r + r_total) * cos(s * angle)))
            all_verts[vert_count] = {'pos': new_pos, 'v_color': color}
            vert_count += 1
        r_total +=  r
        c = 1 #side number we are on in loop
        if level == 1:
            for each in range(sides):
                if c < sides:
                    ind_ext((c, 0, c+1))
                else:
                    ind_ext((c, 0, 1))
                ind_count += 3
                c += 1
        else:
            for each in range(sides):
                offset = sides*(i-1)
                if c < sides:
                    ind_ext((c+sides+offset, c+sides+1+offset, c+offset))
                    ind_ext((c+offset, c+1+offset, c+sides+1+offset))
                else:
                    ind_ext((c+sides+offset, sides+1+offset, sides+offset))
                    ind_ext((sides+offset, 1+offset, sides+1+offset))
                ind_count += 6
                c += 1
        i += 1
    return {'indices': indices, 'vertices': all_verts, 
        'vert_count': vert_count, 'ind_count': ind_count}
