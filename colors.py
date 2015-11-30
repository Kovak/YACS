from random import choice, uniform, randrange

color_palettes = {
    'violot': {
        1: (246, 225, 255),
        2: (235, 192, 253),
        3: (173, 0, 242),
        4: (111, 42, 124),
        5: (28, 19, 27),
    },
    'indigo': {
        1: (233, 225, 255),
        2: (200, 181, 252),
        3: (89, 29, 255),
        4: (72, 49, 142),
        5: (32, 29, 41),
    },
    'blue': {
        1: (225, 241, 255),
        2: (190, 223, 253),
        3: (43, 153, 255),
        4: (49, 87, 135),
        5: (28, 32, 40),
    },
    'aqua': {
        1: (225, 255, 249),
        2: (190, 254, 243),
        3: (0, 221, 176),
        4: (30, 91, 78),
        5: (21, 30, 28),
    },
    'green': {
        1: (233, 255, 225),
        2: (214, 254, 188),
        3: (93, 226, 0),
        4: (76, 116, 33),
        5: (34, 41, 29),
    },
    'yellow': {
        1: (252, 255, 225),
        2: (249, 254, 186),
        3: (223, 251, 63),
        4: (155, 147, 41),
        5: (41, 44, 20),
    },
    'orange': {
        1: (255, 239, 225),
        2: (253, 220, 189),
        3: (255, 123, 8),
        4: (149, 65, 42),
        5: (58, 29, 22),
    },
}

color_choices = [key for key in color_palettes]
sun_choices = ['orange', 'yellow', 'aqua', 'blue']

def gen_star_color_levels(color):
    color_palette = color_palettes[color]
    color0 = list(color_palette[1])
    color0.append(255)
    color1 = list(color_palette[2])
    color1.append(255)
    color2 = list(color_palette[3])
    color2.append(255)

    return {0: color0, 1: color1, 2: color2, 3: (color2[0], color2[1], 
        color2[3], 0)}

def gen_color_palette(divisions, color1, color2, max_step, color_swaps, 
    do_alpha=False, alpha_low_cutoff=0., alpha_high_cutoff=1., 
    alpha_range=(100, 200), level_choices=[1, 2, 3, 4, 5]):
    current_point = 0.
    palette = []
    pal_a = palette.append
    swap_every = divisions // color_swaps
    swap_count = 0
    current_color = color1
    current_level = 5
    direction_choices = [0, 1, 1]
    direction = 0
    for x in range(divisions):
        color = list(color_palettes[current_color][current_level])
        if do_alpha:
            if current_point < alpha_low_cutoff or (
            current_point > alpha_high_cutoff):
                alpha_v = 0
            else:
                alpha_v = randrange(alpha_range[0], alpha_range[1])
            color.append(alpha_v)
        pal_a((current_point, color))
        current_point = uniform(current_point + max_step/2., 
            current_point + max_step)
        if x == divisions - 2:
            current_point = 1.
        if current_point > 1.:
            current_point == 1.
        last_level = current_level
        while current_level == last_level:
            current_level = choice(level_choices)
        swap_count += 1
        if swap_count >= swap_every:
            swap_count = 0
            if current_color == color1:
                current_color = color2
            else:
                current_color = color1
    return palette