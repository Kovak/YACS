from kivent_core.systems.gamesystem import GameSystem
from kivy.factory import Factory
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from grid_generation import load_grid, generate_grid
from background_generator import ZoneInfo
from random import random, randint, choice, uniform, randrange, sample, seed
from math import radians
from kivent_core.managers.resource_managers import texture_manager
from utils import get_asset_path
from colors import color_choices

class GlobalMapSystem(GameSystem):
    world_size = NumericProperty(10)
    margin = NumericProperty(100.)
    system_id = StringProperty('global_map')
    do_components = BooleanProperty(False)
    world_x = NumericProperty(0)
    world_y = NumericProperty(0)
    cell_size = NumericProperty(150.)
    grid_border_width = NumericProperty(0.)
    grid_line_width = NumericProperty(2.)
    grid_fade_width = NumericProperty(1.)

    def __init__(self, **kwargs):
        super(GlobalMapSystem, self).__init__(**kwargs)
        self.zone_infos = {}
        self.star_names = {}
        self.visited = []

    def setup(self, world_seed, background_generator):
        self.world_seed = world_seed
        self.background_generator = background_generator
        self.setup_grid()
        self.setup_map_stars()
        self.setup_zones()
        self.setup_map_asteroids()
        self.setup_unexplored_icon()
        self.setup_map_planets()

    def add_zone_to_visited(self, zone_pos):
        self.visited.append(zone_pos)

    def setup_unexplored_icon(self):
        texture_name = texture_manager.load_image(
            get_asset_path('assets', 'ui_elements', 'unexplored-icon.png')
            )
        model_manager = self.gameworld.model_manager
        self.unexplored_icon = model_manager.load_textured_rectangle(
            'vertex_format_4f', 64, 64, 'unexplored-icon',
            '4f_unexplored-icon',
            )
        model = model_manager.models[self.unexplored_icon]
        vt1 = model[0]
        vt2 = model[1]
        vt3 = model[2]
        vt4 = model[3]
        u1, v1 = vt1.uvs
        u2, v2 = vt2.uvs
        u3, v3 = vt3.uvs
        u4, v4 = vt4.uvs
        vt1.uvs = (u1, v3)
        vt2.uvs = (u2, v4)
        vt3.uvs = (u3, v1)
        vt4.uvs = (u4, v2)
        self.unexplored_texture = 'unexplored-icon'


    def setup_grid(self):
        outer_color = [150, 0, 100, 100]
        inner_color = [150, 0, 100, 255]
        grid_size = self.world_size
        actual_size = grid_size*self.cell_size, grid_size*self.cell_size
        actual_pos = (0., 0.)
        grid_offset, grid_data, cell_size = generate_grid(
                                               self.grid_border_width,
                                               self.grid_line_width,
                                               self.grid_fade_width,
                                               actual_size,
                                               actual_pos, grid_size + 1,
                                               outer_color, inner_color
                                               )
        self.actual_cell_size = cell_size
        self.grid_model = load_grid(self.gameworld, grid_data, 'world_grid')
        self.grid_offset = grid_offset

    def setup_map_planets(self):
        world_seed = self.world_seed
        seed(world_seed.get_global_map_planet_seed())
        background_generator = self.background_generator
        planets = {}
        model_manager = self.gameworld.model_manager
        planets['small'] = background_generator.generate_planets(
                                    100, 100, 100, 40,
                                    'small_map_planet',
                                    'triangulated_models/circle_100_10.kem',
                                    )
        for model_name in planets['small']:
            background_generator.draW_planet_simple(model_name, 150,
                                                    choice(color_choices),
                                                    choice(color_choices))
            model = model_manager.models[model_name]
            model.mult_all_vertex_attribute('pos', uniform(.04, .06))
        planets['medium_small'] = background_generator.generate_planets(
                                    100, 100, 100, 30,
                                    'medium_small_map_planet',
                                    'triangulated_models/circle_100_10.kem',
                                    )
        for model_name in planets['medium_small']:
            background_generator.draW_planet_simple(model_name, 150,
                                                    choice(color_choices),
                                                    choice(color_choices))
            model = model_manager.models[model_name]
            model.mult_all_vertex_attribute('pos', uniform(.06, .08))
        planets['medium_large'] = background_generator.generate_planets(
                                    100, 100, 100, 30,
                                    'medium_large_map_planet',
                                    'triangulated_models/circle_100_10.kem',
                                    )
        for model_name in planets['medium_large']:
            background_generator.draW_planet_simple(model_name, 150,
                                                    choice(color_choices),
                                                    choice(color_choices))
            model = model_manager.models[model_name]
            model.mult_all_vertex_attribute('pos', uniform(.08, .1))
        planets['large'] = background_generator.generate_planets(
                                    100, 100, 100, 20,
                                    'large_map_planet',
                                    'triangulated_models/circle_100_10.kem',
                                    )
        for model_name in planets['large']:
            background_generator.draW_planet_simple(model_name, 150,
                                                    choice(color_choices),
                                                    choice(color_choices))
            model = model_manager.models[model_name]
            model.mult_all_vertex_attribute('pos', uniform(.1, .12))
        self.planets = planets


    def setup_map_stars(self):
        stars = self.star_names
        background_generator = self.background_generator
        generate_star = background_generator.generate_star
        generate_offset_star = background_generator.generate_offset_star
        stars['small_star'] = generate_star('small_map_star', 4, 'blue', 3.5)
        stars['med_small_star'] = generate_star('med_small_map_star', 34,
                                                'blue', 4.5)
        stars['medium_star'] = generate_offset_star('medium_map_star', 16,
                                                    'blue', 4.0, 5.0)
        stars['large_star'] = generate_offset_star('large_star', 24,
                                                   'blue', 4., 5.5)

    def setup_map_asteroids(self):
        model_manager = self.gameworld.model_manager
        self.asteroid_model = model_manager.load_textured_rectangle(
            'vertex_format_4f', 14, 14, 'asteroid1-radar', '4f_asteroid_map',
            )
        self.asteroid_texture = 'asteroid1-radar'

    def draw_unexplored_icon(self, pos):
        create_dict = {
            'position': pos,
            'rotate': 0.,
            'color': (255, 255, 255, 255),
            'global_map_renderer2': {'model_key': self.unexplored_icon,
                                     'texture': self.unexplored_texture}
        }
        self.gameworld.init_entity(create_dict,
                                   ['position', 'rotate', 'color', 
                                    'global_map_renderer2'])

    def draw_planet(self, pos, planet_model):
        create_dict = {
            'position': pos,
            'global_map_planet_renderer': {'model_key': planet_model}
        }
        self.gameworld.init_entity(create_dict,
                                   ['position', 'global_map_planet_renderer'])

    def draw_asteroid(self, pos, rotate):
        create_dict = {
            'position': pos,
            'rotate': rotate,
            'color': (155, 155, 155, 255),
            'global_map_renderer2': {'model_key': self.asteroid_model,
                                     'texture': self.asteroid_texture}
        }
        self.gameworld.init_entity(create_dict,
                                   ['position', 'rotate', 'color',
                                    'global_map_renderer2'])


    def draw_map(self):
        world_seed = self.world_seed
        seed(world_seed.get_global_map_seed())
        self.create_world_grid()
        zones = self.zone_infos
        draw_star = self.draw_star
        draw_asteroid = self.draw_asteroid
        draw_unexplored_icon = self.draw_unexplored_icon
        draw_planet = self.draw_planet
        get_bounds_for_cell = self.get_bounds_for_cell
        star_names = self.star_names
        small_star_name = star_names['small_star']
        med_small_name = star_names['med_small_star']
        med_star_name = star_names['medium_star']
        large_star_name = star_names['large_star']
        cell_size = self.cell_size
        small_planet_choices = self.planets['small']
        medium_small_choices = self.planets['medium_small']
        medium_large_choices = self.planets['medium_large']
        large_choices = self.planets['large']
        visited = self.visited
        for zone_key in zones:
            zone = zones[zone_key]
            x0, y0, x1, y1 = get_bounds_for_cell(zone_key)
            h = y1 - y0
            w = x1 - x0
            if True:
                x0 += w * .2
                y0 += h * .2
                x1 -= w * .2
                y1 -= h * .2
                for x in range(zone.small_suns):
                    draw_star((uniform(x0, x1), uniform(y0, y1)),
                              small_star_name)
                for x in range(zone.medium_small_suns):
                    draw_star((uniform(x0, x1), uniform(y0, y1)),
                              med_small_name)
                for x in range(zone.medium_large_suns):
                    draw_star((uniform(x0, x1), uniform(y0, y1)),
                              med_star_name)
                for x in range(zone.large_suns):
                    draw_star((uniform(x0, x1), uniform(y0, y1)),
                              large_star_name)
                for x in range(int(zone.asteroid_count//30)):
                    draw_asteroid((uniform(x0, x1), uniform(y0, y1)),
                                  radians(uniform(0., 360.)))
                for x in range(zone.small_planets):
                    draw_planet((uniform(x0, x1), uniform(y0, y1)),
                                choice(small_planet_choices))
                for x in range(zone.medium_small_planets):
                    draw_planet((uniform(x0, x1), uniform(y0, y1)),
                                choice(medium_small_choices))
                for x in range(zone.medium_large_planets):
                    draw_planet((uniform(x0, x1), uniform(y0, y1)),
                                choice(medium_large_choices))
                for x in range(zone.large_planets):
                    draw_planet((uniform(x0, x1), uniform(y0, y1)),
                                choice(large_choices))

            else:
                draw_unexplored_icon((x0 + .5 * w, y0 + .5 * h))

    def draw_star(self, pos, star_name):
        create_dict = {
            'position': pos,
            'global_map_renderer': {'model_key': star_name}
        }
        self.gameworld.init_entity(create_dict,
                                   ['position', 'global_map_renderer'])

    def setup_zones(self):
        world_seed = self.world_seed
        zones = self.zone_infos
        for x in range(self.world_size):
            for y in range(self.world_size):
                zones[(x, y)] = zone = ZoneInfo(world_seed, x, y)

    def get_cell_pos_from_world_pos(self, pos):
        x, y = pos
        return int(x // self.cell_size), int(y // self.cell_size)

    def get_bounds_for_cell(self, cell_pos):
        cx, cy = cell_pos
        line_space = self.grid_fade_width + self.grid_line_width
        cell_size = self.actual_cell_size + line_space
        return (cx * cell_size, cy * cell_size,
               (cx + 1) * cell_size, (cy + 1) * cell_size)

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