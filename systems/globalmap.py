from kivent_core.systems.gamesystem import GameSystem
from kivy.factory import Factory
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from grid_generation import load_grid, generate_grid
from background_generator import ZoneInfo
from random import random, randint, choice, uniform, randrange, sample, seed

class GlobalMapSystem(GameSystem):
    world_size = NumericProperty(10)
    margin = NumericProperty(100.)
    system_id = StringProperty('global_map')
    do_components = BooleanProperty(False)
    world_x = NumericProperty(0)
    world_y = NumericProperty(0)
    cell_size = NumericProperty(150.)

    def __init__(self, **kwargs):
        super(GlobalMapSystem, self).__init__(**kwargs)
        self.zone_infos = {}
        self.star_names = {}

    def setup_grid(self):
        outer_color = [150, 0, 100, 100]
        inner_color = [150, 0, 100, 255]
        grid_size = self.world_size
        actual_size = grid_size*self.cell_size, grid_size*self.cell_size
        actual_pos = (0., 0.)
        grid_offset, grid_data = generate_grid(0., 2., 1., actual_size,
                                               actual_pos, grid_size,
                                               outer_color, inner_color)
        self.grid_model = load_grid(self.gameworld, grid_data, 'world_grid')
        self.grid_offset = grid_offset

    def setup_map_stars(self, background_generator):
        stars = self.star_names
        generate_star = background_generator.generate_star
        generate_offset_star = background_generator.generate_offset_star
        stars['small_star'] = generate_star('small_map_star', 4, 'blue', 3.5)
        stars['med_small_star'] = generate_star('med_small_map_star', 34,
                                                'blue', 4.5)
        stars['medium_star'] = generate_offset_star('medium_map_star', 16,
                                                    'blue', 4.0, 5.0)
        stars['large_star'] = generate_offset_star('large_star', 24,
                                                   'blue', 4.75, 5.5)

    def draw_map(self, world_seed):
        seed(world_seed.get_global_map_seed())
        self.create_world_grid()
        zones = self.zone_infos
        draw_star = self.draw_star
        get_bounds_for_cell = self.get_bounds_for_cell
        star_names = self.star_names
        small_star_name = star_names['small_star']
        med_small_name = star_names['med_small_star']
        med_star_name = star_names['medium_star']
        large_star_name = star_names['large_star']
        cell_size = self.cell_size
        for zone_key in zones:
            zone = zones[zone_key]
            x0, y0, x1, y1 = get_bounds_for_cell(zone_key)
            x0 += cell_size * .1
            y0 += cell_size * .1
            x1 -= cell_size * .1
            y1 -= cell_size * .1
            for x in range(zone.small_suns):
                draw_star((uniform(x0, x1), uniform(y0, y1)), small_star_name)
            for x in range(zone.medium_small_suns):
                draw_star((uniform(x0, x1), uniform(y0, y1)), med_small_name)
            for x in range(zone.medium_large_suns):
                draw_star((uniform(x0, x1), uniform(y0, y1)), med_star_name)
            for xi in range(zone.large_suns):
                draw_star((uniform(x0, x1), uniform(y0, y1)), large_star_name)

    def draw_star(self, pos, star_name):
        create_dict = {
            'position': pos,
            'global_map_renderer': {'model_key': star_name}
        }
        self.gameworld.init_entity(create_dict,
                                   ['position', 'global_map_renderer'])

    def setup_zones(self, world_seed):
        zones = self.zone_infos
        for x in range(self.world_size):
            for y in range(self.world_size):
                zones[(x, y)] = zone = ZoneInfo(world_seed, x, y)

    def get_cell_pos_from_world_pos(self, pos):
        x, y = pos
        return int(x // self.cell_size), int(y // self.cell_size)

    def get_bounds_for_cell(self, cell_pos):
        cx, cy = cell_pos
        return (cx * self.cell_size, cy * self.cell_size,
               (cx + 1) * self.cell_size, (cy + 1) * self.cell_size)

    def on_touch_down(self, touch):
        cell_pos = self.get_cell_pos_from_world_pos(touch.pos)


    def create_world_grid(self):
        create_dict = {
            'position': self.grid_offset,
            'world_grid': {'model_key': self.grid_model},
            }
        ent = self.gameworld.init_entity(
            create_dict, 
            ['position', 'world_grid'])
        return ent


Factory.register("GlobalMapSystem", cls=GlobalMapSystem)