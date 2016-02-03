from geometry import draw_layered_regular_polygon

def generate_shield_model(radius, width):
    radius_color_dict = {1: (radius, (255, 255, 255, 0)),
                         2: (2., (255, 255, 255, 0)),
                         2: (.4*width, (255, 255, 255, 125)),
                         3: (.1*width, (255, 255, 255, 255)),
                         4: (.4*width, (255, 255, 255, 125)),
                         5: (2.,(255, 255, 255, 0))}
    return draw_layered_regular_polygon((0., 0.), 5, 32, (0, 0, 0, 0),
                                        radius_color_dict)