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

def draw_colored_layered_grid(spacing, line_width, fade_width, cells, color, 
    middle_color, fade_color):
    #draw centered around 0, 0
    pos = (0, 0)
    hs = spacing/2.
    hf = fade_width/2.
    line_spacing = line_width+fade_width
    total_size = line_spacing*cells + spacing*(cells)
    print('total size is', total_size)
    total_gap = total_size/cells
    starting_pos = (
        pos[0] + line_spacing/2. + hs - total_size/2., 
        pos[1] + line_spacing/2. + hs - total_size/2.
        )
    all_verts = {}
    indices = []
    vert_count = 0
    ind_count = 0
    ind_e = indices.extend
    for x_count in range(cells):
        for y_count in range(cells):
            x_offset = total_gap*x_count
            y_offset = total_gap*y_count
            vert_count += 17
            initial_point = (
                starting_pos[0] + x_offset, starting_pos[1] + y_offset)
            ix, iy = initial_point
            a = 17*x_count + 17*y_count*cells
            prev_ax = a - 17
            prev_ay = a - 17*cells
            # calculate vertex positions
            a_vert = {'pos': (ix, iy), 'v_color': middle_color}
            b_vert = {'pos': (ix - hs, iy - hs), 'v_color': color}
            c_vert = {'pos': (ix, iy - hs), 'v_color': middle_color}
            d_vert = {'pos': (ix + hs, iy - hs), 'v_color': color}
            e_vert = {'pos': (ix - hs, iy), 'v_color': middle_color}
            f_vert = {'pos': (ix + hs, iy), 'v_color': middle_color}
            g_vert = {'pos': (ix - hs, iy + hs), 'v_color': color}
            h_vert = {'pos': (ix, iy + hs), 'v_color': middle_color}
            i_vert = {'pos': (ix + hs, iy + hs), 'v_color': color}
            j_vert = {'pos': (ix - hs - hf, iy - hs - hf), 
                'v_color': fade_color}
            k_vert = {'pos': (ix, iy - hs - hf), 'v_color': fade_color}
            l_vert = {'pos': (ix + hs + hf, iy - hs - hf), 
                'v_color': fade_color}
            m_vert = {'pos': (ix - hs - hf, iy), 'v_color': fade_color}
            n_vert = {'pos': (ix + hs + hf, iy), 'v_color': fade_color}
            o_vert = {'pos': (ix - hs - hf, iy + hs + hf), 
                'v_color': fade_color}
            p_vert = {'pos': (ix, iy + hs + hf), 'v_color': fade_color}
            q_vert = {'pos': (ix + hs + hf, iy + hs + hf), 
                'v_color': fade_color}
            # calculate indexes
            b = a+1
            c = a+2
            d = a+3
            e = a+4
            f = a+5
            g = a+6
            h = a+7
            i = a+8
            j = a+9
            k = a+10
            l = a+11
            m = a+12
            n= a+13
            o = a+14
            p = a+15
            q = a+16
            all_verts[a] = a_vert
            all_verts[b] = b_vert
            all_verts[c] = c_vert
            all_verts[d] = d_vert
            all_verts[e] = e_vert
            all_verts[f] = f_vert
            all_verts[g] = g_vert
            all_verts[h] = h_vert
            all_verts[i] = i_vert
            all_verts[j] = j_vert
            all_verts[k] = k_vert
            all_verts[l] = l_vert
            all_verts[m] = m_vert
            all_verts[n] = n_vert
            all_verts[o] = o_vert
            all_verts[p] = p_vert
            all_verts[q] = q_vert
            if x_count > 0:
                pxf = prev_ax+5
                pxi = prev_ax+8
                pxd = prev_ax+3
                ind_e([pxf, pxi, g, g, pxf, e, e, b, pxf, pxf, pxd, b])
                ind_count += 12
            if y_count > 0:
                pyh = prev_ay+7
                pyg = prev_ay+6
                pyi = prev_ay+8
                ind_e([pyh, pyg, b, b, c, pyh, pyh, pyi, d, d, pyh, c])
                ind_count += 12
            ind_e([
                a, e, c,
                c, b, e,
                e, g, h,
                h, e, a,
                a, f, h,
                h, i, f,
                f, a, c,
                c, d, f,])
            ind_count += 24
            if x_count == 0 and y_count == 0:
                ind_e([
                    m, e, b,
                    b, m, j,
                    j, b, k,
                    k, b, c,
                    m, e, g,
                    g, m, o,
                    c, d, k,
                    k, l, d,
                    ])
                ind_count += 24
            if x_count == cells-1 and y_count == cells-1:
                ind_e([
                    o, p, g,
                    g, p, h,
                    h, p, i,
                    i, p, q,
                    q, i, n,
                    n, i, f,
                    f, n, d,
                    d, n, l,
                    ])
                ind_count += 24
            if x_count == cells-1 and y_count == 0:
                ind_e([
                    q, n, i,
                    i, n, f,
                    f, n, d,
                    d, n, l,
                    l, d, k,
                    k, d, c,
                    c, k, b,
                    b, k, j
                    ])
                ind_count += 24
            if x_count == 0 and y_count == cells-1:
                ind_e([
                    j, b, m,
                    m, b, e,
                    e, m, g,
                    g, m, o,
                    o, g, p,
                    p, g, h,
                    h, p, i,
                    i, p, q,
                    ])
                ind_count += 24
            if y_count > 0 and 0 <= x_count <= cells-1:
                pyo = prev_ay+14
                pyg = prev_ay+6
                pyq = prev_ay+16
                pyi = prev_ay+8
                ind_e([
                    j, b, pyg,
                    pyg, j, pyo,
                    d, l, pyi,
                    pyi, l, pyq,
                    ])
                ind_count += 12
            if x_count > 0 and 0 <= y_count <= cells-1:
                pxi = prev_ax+8
                pxq = prev_ax+16
                pxl = prev_ax+11
                pxd = prev_ax+3
                ind_e([
                    pxd, pxl, j,
                    j, pxd, b,
                    pxq, pxi, o, 
                    o, pxi, g
                    ])
                ind_count += 12
            if y_count == 0 and 0 < x_count < cells-1:
                ind_e([
                    b, j, k,
                    k, b, c,
                    c, d, k,
                    k, d, l,
                    ])
                ind_count += 12
            if x_count == 0 and 0 < y_count < cells-1:
                ind_e([
                    g, o, m,
                    m, g, e,
                    e, m, b,
                    b, m, j,
                    ])
                ind_count += 12
            if y_count == cells-1 and 0 < x_count < cells-1:
                ind_e([
                    o, g, p,
                    p, g, h,
                    h, p, i,
                    i, p, q,
                    ])
                ind_count += 12
            if x_count == cells-1 and 0 < y_count < cells-1:
                ind_e([
                    q, i, n,
                    n, i, f,
                    f, n, d,
                    d, n, l,
                    ])
                ind_count += 12

    return {'indices': indices, 'vertices': all_verts, 
        'vert_count': vert_count, 'ind_count': ind_count}


def draw_irregular_polygon(points, color):
    center = (0., 0.)
    vertices = {}
    vertices[0] = {'pos': center, 'v_color': color}
    indices = []
    count = len(points)
    for index, point in enumerate(points):
        vertices[index+1] = {'pos': point, 'v_color': color}
        if index < count:
            indices.extend([0, index+1, index+2])
        else:
            indices.extend([index+1, 0, 1])
    return {'indices': indices, 'vertices': vertices, 
            'vert_count': len(vertices), 'ind_count': len(indices)}


def draw_colored_grid(pos, spacing, width, cells, color, middle_color):
    total_gap = width+spacing
    total_size = total_gap*cells
    hs = spacing/2.
    starting_pos = pos[0] - total_size/2., pos[1] - total_size/2.
    all_verts = {}
    indices = []
    vert_count = 0
    ind_count = 0
    ind_e = indices.extend
    for x_count in range(cells):
        for y_count in range(cells):
            x_offset = total_gap*x_count
            y_offset = total_gap*y_count
            vert_count += 9
            initial_point = (
                starting_pos[0] + x_offset, starting_pos[1] + y_offset)
            ix, iy = initial_point
            a = 9*x_count + 9*y_count*cells
            prev_ax = a - 9
            prev_ay = a - 9*cells
            # calculate vertex positions
            a_vert = {'pos': (ix, iy), 'v_color': middle_color}
            b_vert = {'pos': (ix - hs, iy - hs), 'v_color': color}
            c_vert = {'pos': (ix, iy - hs), 'v_color': middle_color}
            d_vert = {'pos': (ix + hs, iy - hs), 'v_color': color}
            e_vert = {'pos': (ix - hs, iy), 'v_color': middle_color}
            f_vert = {'pos': (ix + hs, iy), 'v_color': middle_color}
            g_vert = {'pos': (ix - hs, iy + hs), 'v_color': color}
            h_vert = {'pos': (ix, iy + hs), 'v_color': middle_color}
            i_vert = {'pos': (ix + hs, iy + hs), 'v_color': color}
            # calculate indexes
            b = a+1
            c = a+2
            d = a+3
            e = a+4
            f = a+5
            g = a+6
            h = a+7
            i = a+8
            all_verts[a] = a_vert
            all_verts[b] = b_vert
            all_verts[c] = c_vert
            all_verts[d] = d_vert
            all_verts[e] = e_vert
            all_verts[f] = f_vert
            all_verts[g] = g_vert
            all_verts[h] = h_vert
            all_verts[i] = i_vert
            if x_count > 0:
                pxf = prev_ax+5
                pxi = prev_ax+8
                pxd = prev_ax+3
                ind_e([pxf, pxi, g, g, pxf, e, e, b, pxf, pxf, pxd, b])
                ind_count += 12
            if y_count > 0:
                pyh = prev_ay+7
                pyg = prev_ay+6
                pyi = prev_ay+8
                ind_e([pyh, pyg, b, b, c, pyh, pyh, pyi, d, d, pyh, c])
                ind_count += 12
            ind_e([
                a, e, c,
                c, b, e,
                e, g, h,
                h, e, a,
                a, f, h,
                h, i, f,
                f, a, c,
                c, d, f])
            ind_count += 24
    return {'indices': indices, 'vertices': all_verts, 
        'vert_count': vert_count, 'ind_count': ind_count}
