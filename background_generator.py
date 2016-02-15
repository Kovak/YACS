from random import random, randint, choice, uniform, randrange, sample, seed
from bisect import bisect_left, bisect_right
from geometry import (
    draw_offset_layered_regular_polygon,
    draw_layered_regular_polygon
    )
from kivent_core.rendering.model import VertexModel
from kivent_noise.noise import scaled_octave_noise_2d

from colors import (
    gen_star_color_levels, gen_color_palette,
    sun_choices, color_choices, get_color1_choice_from_val,
    get_color2_choice_from_val
    )
from utils import lerp_color, iweighted_choice

class NoiseInfo(object):

    def __init__(self, octaves, persistance, scale):
        self.octaves = octaves
        self.persistance = persistance
        self.scale = scale

class ZoneInfo(object):

    def __init__(self, world_seed, x, y):
        seed(world_seed.get_seed_for_zone(x, y))
        map_size = world_seed.map_size
        cx_noise = world_seed.color_x_noise
        cy_noise = world_seed.color_y_noise
        star_noise = world_seed.star_count_noise
        asteroid_noise = world_seed.asteroid_count_noise
        self.offset = offset = (map_size[0] * x, map_size[1] * y)
        color1_val = scaled_octave_noise_2d(cx_noise.octaves, 
                                            cx_noise.persistance,
                                            cx_noise.scale, 0., 1.,
                                            offset[0],  offset[1])
        color2_val = scaled_octave_noise_2d(cy_noise.octaves, 
                                            cy_noise.persistance,
                                            cy_noise.scale, 0., 1.,
                                            offset[0], offset[1])
        star_val = scaled_octave_noise_2d(star_noise.octaves,
                                          star_noise.persistance,
                                          star_noise.scale, 0., 1.,
                                          offset[0], offset[1])
        asteroid_val = scaled_octave_noise_2d(asteroid_noise.octaves,
                                              asteroid_noise.persistance,
                                              asteroid_noise.scale, 0., 1.,
                                              offset[0], offset[1])
        band_min = world_seed.asteroid_band_min
        band_max = world_seed.asteroid_band_max
        if band_min <= asteroid_val <= band_max:
            band_width = band_max - band_min
            offset_val = asteroid_val - band_min
            actual_val = offset_val / band_width
            asteroid_count = int(world_seed.max_asteroids * actual_val)
        else:
            asteroid_count = 0
        self.asteroid_count = asteroid_count
        self.color1 = get_color1_choice_from_val(color1_val)
        self.color2 = get_color2_choice_from_val(color2_val)
        self.star_count = int(world_seed.max_stars * star_val)
        self.small_planets = iweighted_choice([(0, 4), (1, 3), (2, 2), (3, 1),
                                               (4, 1)])
        self.medium_small_planets = iweighted_choice([(1, 2), (2, 1), (0, 3)])
        self.medium_large_planets = iweighted_choice([(1, 2), (2, 1), (0, 10)])
        self.large_planets = iweighted_choice([(1, 1), (0, 13)])
        self.small_suns = iweighted_choice([(2, 1), (1, 3), (0, 6)])
        self.medium_small_suns = iweighted_choice([(1, 1), (0, 6)])
        self.medium_large_suns = iweighted_choice([(1, 1), (0, 9)])
        self.large_suns = iweighted_choice([(1, 1), (0, 15)])
 
class WorldSeed(object):

    def __init__(self, world_seed, map_size):
        self.world_seed = world_seed
        seed(world_seed)
        self.max_stars = 15000
        self.max_asteroids = 300
        self.map_size = map_size
        self.asteroid_band_min = uniform(.25, .4)
        self.asteroid_band_max = uniform(.45, .75)
        self.color_x_noise = NoiseInfo(randint(4, 16), uniform(.3, .7),
                                       uniform(.004, .009))
        self.color_y_noise = NoiseInfo(randint(4, 16), uniform(.3, .7),
                                       uniform(.004, .009))
        self.star_count_noise = NoiseInfo(randint(4, 16), uniform(.5, .9),
                                          uniform(.003, .006))
        self.asteroid_count_noise = NoiseInfo(8, uniform(.2, .4),
                                              uniform(.001, .004))

    def get_seed_for_zone(self, x, y):
        return self.world_seed + '_' + str(x) + '_' + str(y)

    def get_global_map_seed(self):
        return self.world_seed + '_global_map'

    def get_global_map_planet_seed(self):
        return self.world_seed + '_global_map_planet_seed'



class PlanetModel(object):

    def __init__(self, name, radius, cloud_name):
        self.radius = radius 
        self.name = name
        self.cloud_name = cloud_name

class BackgroundGenerator(object):

    def __init__(self, gameworld, **kwargs):
        self.gameworld = gameworld
        super(BackgroundGenerator, self).__init__(**kwargs)
        self.planet_register = {}


    def generate(self):
        star_names = self.generate_stars(1., 4., 5., sun_choices, 20,
                                         10, 10, 20, 30)
        self.star_names = star_names
        self.planet_names = planet_names = {}
        planet_names['small_planets'] = self.generate_planets(
            100., 75., 125., 10, 
            'small_planet','triangulated_models/circle_100_10.kem'
            )
        planet_names['medium_small_planets'] = self.generate_planets(
            200., 175., 350., 5,
            'medium_small_planet', 'triangulated_models/circle_200_10.kem'
            )
        planet_names['medium_large_planets'] = self.generate_planets(
            400., 375., 600., 5,
            'medium_large_planet', 'triangulated_models/circle_400_30.kem'
            )
        planet_names['large_planets'] = self.generate_planets(
            800., 650., 850., 5, 
            'large_planet', 'triangulated_models/circle_800_50.kem'
            )

    def populate_model_with_noise(self, model_name, octaves, 
                                  persistence, scale, offset, radius, colors, 
                                  transparent_level = 0., default_alpha = 255):
        model_manager = self.gameworld.model_manager
        model = model_manager.models[model_name]
        vertices = model.vertices
        r2 = radius*radius
        ox, oy = offset
        col_keys = [x[0] for x in colors]
        def distance_from_center(pos, center=(0.,0.)):
            x_dist = pos[0] - center[0]
            y_dist = pos[1] - center[1]
            return x_dist*x_dist + y_dist*y_dist
        for vertex in vertices:
            pos = x,y = vertex.pos
            if distance_from_center(pos) > r2:
                zcolor = colors[0][1]
                vertex.v_color = [zcolor[0], zcolor[1], zcolor[2], 0]
            else:
                noise = scaled_octave_noise_2d(octaves, persistence, scale, 0., 
                    1., x+ox, y+oy)
                col_bisect = bisect_left(col_keys, noise)
                left = colors[col_bisect-1]
                right = colors[col_bisect]
                t = (noise - left[0]) / (right[0] - left[0])
                new_color = lerp_color(left[1], right[1], t)
                if len(new_color) == 3:
                    new_color.append(default_alpha)
                if noise < transparent_level:
                    new_color[3] = 0
                vertex.v_color = new_color

    def draw_sun(self, model_name, color_choice, radius):
        divisions = randint(6, 12)
        even_div = 1.0 / divisions
        colors = gen_color_palette(
            divisions, color_choice, 
            color_choice, uniform(even_div, 2*even_div), randint(1, 6),
            level_choices=[(1, 6), (2, 1), (3, 1)]
            )
        self.populate_model_with_noise(
            model_name, 16, uniform(.5, .9),
            uniform(.03, .05), (uniform(radius, 10000.), 
            uniform(radius, 10000.)), radius, colors
            )

    def generate_star(self, model_name, sides, color, max_radius, 
                      do_copy=False):
        colors = gen_star_color_levels(color)
        first_r = uniform(.5, .9)
        final_r = uniform(.01, .1)
        total = first_r + final_r
        remainder = 1.0 - total
        middle_r = uniform(final_r, final_r+remainder)
        radius_color_dict = {
            1: (max_radius*first_r, colors[1]),
            2: (max_radius*middle_r, colors[2]),
            3: (max_radius*final_r, colors[3])}
        star_data = draw_layered_regular_polygon((0., 0.), 3, sides, 
            colors[0], radius_color_dict)
        model_manager = self.gameworld.model_manager
        return model_manager.load_model('vertex_format_2f4ub', 
            star_data['vert_count'], star_data['ind_count'], model_name, 
            indices=star_data['indices'], vertices=star_data['vertices'],
            do_copy=do_copy)

    def generate_offset_star(self, model_name, sides, color, max_radius_1, 
                             max_radius_2, do_copy=False):
        colors = gen_star_color_levels(color)
        first_r = uniform(.5, .9)
        final_r = uniform(.01, .1)
        total = first_r + final_r
        remainder = 1.0 - total
        middle_r = uniform(final_r, final_r+remainder)
        radius_color_dict = {
            1: ((max_radius_1*first_r, max_radius_2*first_r), colors[1]),
            2: ((max_radius_1*middle_r, max_radius_2*first_r), colors[2]),
            3: ((max_radius_1*final_r, max_radius_2*final_r), colors[3])}
        star_data = draw_offset_layered_regular_polygon((0., 0.), 3, sides, 
            colors[0], radius_color_dict)
        model_manager = self.gameworld.model_manager
        return model_manager.load_model('vertex_format_2f4ub', 
            star_data['vert_count'], star_data['ind_count'], model_name, 
            indices=star_data['indices'], vertices=star_data['vertices'],
            do_copy=do_copy)

    def draW_planet_simple(self, model_name, radius, color1, color2):
        divisions = randint(6, 12)
        even_div = 1.0 / divisions
        colors = gen_color_palette(divisions, color1, 
                                   color2, uniform(even_div, 2*even_div),
                                   randint(1, 4),
                                   level_choices=[(2, 1), (3, 1), (4, 2),
                                                  (5, 2)],
                                   )
        self.populate_model_with_noise(model_name, 16, uniform(.3, .7),
                                       uniform(.004, .009),
                                       (uniform(radius, radius*4),
                                        uniform(radius, radius*4)),
                                       radius, colors)

    def draw_planet(self, model_name, cloud_name, radius, color1, color2):
        divisions = randint(6, 12)
        even_div = 1.0 / divisions
        colors = gen_color_palette(divisions, color1, 
                                   color2, uniform(even_div, 2*even_div),
                                   randint(1, 4),
                                   level_choices=[(2, 1), (3, 1), (4, 2),
                                                  (5, 2)],
                                   )
        self.populate_model_with_noise(model_name, 16, uniform(.3, .7),
                                       uniform(.004, .009),
                                       (uniform(radius, radius*4),
                                        uniform(radius, radius*4)),
                                       radius, colors)
        divisions = randint(4, 6)
        even_div = 1.0 / divisions
        colors = gen_color_palette(
            divisions, color1, color2, uniform(even_div, 2*even_div), 1,
            level_choices=[(1, 1), (2, 2), (3, 1), (4, 1), (5, 1)],
            do_alpha=True, 
            alpha_low_cutoff=uniform(.2, .5), 
            alpha_high_cutoff=uniform(.6, .9),
            alpha_range=(0, 200)
            )
        self.populate_model_with_noise(
            cloud_name, 8, uniform(.2, .4),
            uniform(.001, .004),
            (uniform(radius, radius*4), uniform(radius, radius*4)), 
            radius, colors
            )

    def generate_planets(self, starting_radius, min_s, max_s, count,
                         model_name, model_file):
        min_scale = min_s/starting_radius
        max_scale = max_s/starting_radius
        model_manager = self.gameworld.model_manager
        model_from_file_name = model_manager.load_model_from_pickle(model_file, 
            model_name=model_name)
        copy_model = model_manager.copy_model
        models = model_manager.models
        cloud_name = model_from_file_name + '_clouds'
        copy_model(model_from_file_name, model_name=cloud_name)
        names = [model_from_file_name]
        names_a = names.append
        planet_register = self.planet_register
        planet_register[model_from_file_name] = PlanetModel(
            model_from_file_name, starting_radius, cloud_name
            )
        for x in range(count-1):
            scale_factor = uniform(min_scale, max_scale)
            new_name = copy_model(model_from_file_name)
            names_a(new_name)
            model = models[new_name]
            cloud_name = new_name + '_clouds'
            planet_register[new_name] = PlanetModel(
                new_name, scale_factor*starting_radius, cloud_name
                )
            model.mult_all_vertex_attribute('pos', scale_factor)
            copy_model(new_name, model_name=cloud_name)
        return names

    def generate_stars(self, min_radius, max_radius, max_offset_radius, 
                       color_choices, four_side_count, offset_count,
                       normal_count, min_sides, max_sides):
        stars = {}
        for color in color_choices:
            stars[color] = c_stars = []
            c_stars_a = c_stars.append
            for x in range(four_side_count):
                model_name = 'star_4_' + str(x)
                radius = uniform(min_radius, max_radius)
                c_stars_a(
                    self.generate_star(model_name, 4, color, 
                    radius, do_copy=True)
                    )
            for x in range(normal_count):
                side_count = randrange(min_sides, max_sides)
                if side_count % 2 == 1:
                    side_count += 1
                model_name = 'star_' + str(side_count) + '_' + str(x)
                radius = uniform(min_radius, max_radius)
                c_stars_a(
                    self.generate_star(model_name, side_count, color, 
                    radius, do_copy=True)
                    )
            for x in range(offset_count):
                side_count = randrange(min_sides, max_sides)
                if side_count % 2 == 1:
                    side_count += 1
                model_name = 'star_' + str(side_count) + '_' + str(x)
                radius1 = uniform(min_radius, max_radius)
                radius2 = uniform(min_radius, max_offset_radius)
                c_stars_a(
                    self.generate_offset_star(model_name, side_count, 
                    color, radius1, radius2, do_copy=True)
                    )
        return stars


    def draw_map(self, size, offset, star_count, color1, color2, 
                 star_renderer=None,
                 planet_renderer=None,
                 sun_renderer=None,
                 do_stars=True,
                 max_color1_chance=.5, max_color2_chance=.25, 
                 small_p_counts=[(1, 2), (2, 1), (0, 3)],
                 medium_small_p_counts=[(1, 1), (2, 1), (0, 4)], 
                 medium_large_p_counts=[(1, 1), (0, 10)], 
                 large_p_counts=[(1, 1), (0, 13)],
                 small_sun_counts = [(1, 1), (0, 4)],
                 medium_small_sun_counts = [(1, 1), (0, 5)],
                 medium_large_sun_counts = [(1, 1), (0, 10)],
                 large_sun_counts = [(0, 1)],
                 persistence=.3,
                 octaves=8,
                 scale=.003,
                 used_planet_names=None):
        w, h = size
        ox, oy = offset
        if used_planet_names is None:
            used_planet_names = []
        star1_chance = uniform(0, max_color1_chance)
        star2_chance = uniform(0, max_color2_chance)
        star_choices = self.star_names
        star1_choices = star_choices[color1]
        star2_choices = star_choices[color2]
        init_entity = self.gameworld.init_entity
        ent_count = 0
        planet_choices = self.planet_names
        if star_renderer is not None:
            for i in range(star_count):
                chance = random()
                star_name = None
                if 0 < chance < star1_chance:
                    star_name = choice(star1_choices)

                elif star1_chance < chance < star1_chance + star2_chance:
                    star_name = choice(star2_choices)
                if star_name is not None:
                    create_dict = {
                        'position': (uniform(0., w), uniform(0, h)),
                        star_renderer: {'model_key': star_name}
                    }
                    init_entity(create_dict, ['position', star_renderer])
        planet_register = self.planet_register
        if planet_renderer is not None:
            choice_pairs = [
                (small_p_counts, planet_choices['small_planets']), 
                (medium_small_p_counts, planet_choices['medium_small_planets']),
                (medium_large_p_counts, planet_choices['medium_large_planets']),
                (large_p_counts, planet_choices['large_planets'])
                ]
            for counts, choices in choice_pairs:
                for planet_name in sample(choices, iweighted_choice(counts)):
                    if planet_name in used_planet_names:
                        continue
                    used_planet_names.append(planet_name)
                    planet_data = planet_register[planet_name]
                    self.draw_planet(planet_name, planet_data.cloud_name, 
                        planet_data.radius+50., choice(color_choices), 
                        choice(color_choices))
                    planet_pos = (uniform(0., w), uniform(0, h))
                    create_dict = {
                        'position': planet_pos,
                            planet_renderer: {'model_key': planet_name}
                    }
                    self.gameworld.init_entity(create_dict, ['position', 
                        planet_renderer])
                    create_dict = {
                        'position': planet_pos,
                        planet_renderer: {'model_key': planet_data.cloud_name}
                    }
                    self.gameworld.init_entity(create_dict, ['position', 
                        planet_renderer])
        if sun_renderer is not None:
            choice_pairs = [
                (small_sun_counts, planet_choices['small_planets']), 
                (medium_small_sun_counts, 
                    planet_choices['medium_small_planets']),
                (medium_large_sun_counts, 
                    planet_choices['medium_large_planets']),
                (large_sun_counts, planet_choices['large_planets'])
                ]
            for counts, choices in choice_pairs:
                for planet_name in sample(choices, iweighted_choice(counts)):
                    if planet_name in used_planet_names:
                        print('planet name in us', planet_name)
                        continue
                    used_planet_names.append(planet_name)
                    planet_data = planet_register[planet_name]
                    self.draw_sun(planet_name, choice([color1, color2]), 
                        planet_data.radius - 10.)
                    planet_pos = (uniform(0., w), uniform(0, h))
                    create_dict = {
                        'position': planet_pos,
                        sun_renderer: {'model_key': planet_name}
                    }
                    self.gameworld.init_entity(create_dict, ['position', 
                        sun_renderer])
        return used_planet_names

    def generate_map(self, world_seed, x, y):
        zone_info = ZoneInfo(world_seed, x, y)
        color1 = zone_info.color1
        color2 = zone_info.color2
        star_count = zone_info.star_count
        asteroid_count = zone_info.asteroid_count
        offset = zone_info.offset
        map_size = world_seed.map_size
        small_p_count = zone_info.small_planets
        small_1 = small_p_count // 2
        small_2 = small_p_count - small_1
        medium_small_p_count = zone_info.medium_small_planets
        medium_small_1 = medium_small_p_count // 2
        medium_small_2 = medium_small_p_count - medium_small_1
        medium_large_p_count = zone_info.medium_large_planets
        medium_large_1 = medium_large_p_count // 2
        medium_large_2 = medium_large_p_count - medium_large_1
        small_sun_count = zone_info.small_suns
        small_sun_1 = small_sun_count // 2
        small_sun_2 = small_sun_count - small_sun_1
        medium_small_sun_count = zone_info.medium_small_suns
        medium_small_sun_1 = medium_small_sun_count // 2
        medium_small_sun_2 = medium_small_sun_count - medium_small_sun_1       
        medium_large_sun_count = zone_info.medium_large_suns
        medium_large_sun_1 = medium_large_sun_count // 2 
        medium_large_sun_2 = medium_large_sun_count - medium_large_sun_1
        large_sun_count = zone_info.large_suns
        print(zone_info.small_suns, zone_info.medium_small_suns,
              zone_info.medium_large_suns, zone_info.large_suns)
        print(small_sun_1, small_sun_2)

        self.draw_map(
            map_size, offset,
            int(star_count*.5), color1, color2, 
            star_renderer='back_stars')
        used = self.draw_map(
            map_size, offset, 
            int(star_count*.3), color1, color2, 
            star_renderer='mid_stars')
        used = self.draw_map(
            map_size, offset, int(star_count*.1), color1, color2, 
            sun_renderer='sun1', used_planet_names=used,
            small_sun_counts = [(small_sun_1, 1)],
            medium_small_sun_counts = [(medium_small_sun_1, 1)],
            medium_large_sun_counts = [(medium_large_sun_1, 1)],
            large_sun_counts = [(large_sun_count, 1)],
            )
        used = self.draw_map(
            map_size, offset, int(star_count*.1), color1, color2, 
            sun_renderer='sun2', used_planet_names=used,
            small_sun_counts = [(small_sun_2, 1)],
            medium_small_sun_counts = [(medium_small_sun_2, 1)],
            medium_large_sun_counts = [(medium_large_sun_2, 1)],
            large_sun_counts = [(0, 1)],)
        used = self.draw_map(
            map_size, offset,
            0, color1, color2, planet_renderer='planet1', 
            small_p_counts=[(small_1, 1)],
            medium_small_p_counts=[(medium_small_1, 1)], 
            medium_large_p_counts=[(medium_large_1, 1)], 
            large_p_counts=[(0, 1)],
            used_planet_names=used)
        used = self.draw_map(
            map_size, offset,
            0, color1, color2, planet_renderer='planet2',
            small_p_counts=[(small_2, 1)],
            medium_small_p_counts=[(medium_small_2, 1)], 
            medium_large_p_counts=[(medium_large_2, 1)], 
            large_p_counts=[(zone_info.large_planets, 1)],
            used_planet_names=used)
        asteroid_system = self.gameworld.system_manager['asteroids']
        for x in range(asteroid_count):
            x = randrange(0, map_size[0])
            y = randrange(0, map_size[1])
            asteroid_system.spawn_object_from_template('asteroid1', (x, y))
