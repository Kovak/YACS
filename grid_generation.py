from geometry import draw_colored_layered_grid

def load_grid(gameworld, model_data, name, do_copy=True):
    return gameworld.model_manager.load_model('vertex_format_2f4ub',
                                              model_data['vert_count'],
                                              model_data['ind_count'], name,
                                              indices=model_data['indices'],
                                              vertices=model_data['vertices'],
                                              do_copy=do_copy)

def get_grid_sizes(size, pos, cell_count, border_size, line_width, fade_width):
    line_space = (line_width + fade_width)
    border_space = size[0] - 2*border_size, size[1] - 2*border_size
    smallest_edge = min(border_space)
    usable_space = smallest_edge - cell_count*line_space
    cell_size = usable_space/(cell_count-1)
    leftovers = (size[0] - smallest_edge, size[1] - smallest_edge)
    pos = (pos[0] + size[0]/2.,
           pos[1] + size[1]/2.)
    return (cell_size, pos)

def generate_grid(border_width, line_width, line_fade_width, size,
                  pos, cells, outer_color, inner_color):
    cell_size, board_pos = get_grid_sizes(
        size, pos, cells, border_width, line_width, line_fade_width
        )
    grid_data = draw_colored_layered_grid(
        line_width, cell_size, line_fade_width,
        cells, outer_color, inner_color, outer_color[0:3] + [0]
        )
    return board_pos, grid_data, cell_size
