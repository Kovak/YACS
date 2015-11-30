from random import random, randint, choice, random, uniform, randrange, sample
from bisect import bisect_left, bisect_right
from geometry import (
    draw_offset_layered_regular_polygon,
    draw_layered_regular_polygon
    )
from kivent_core.rendering.model import VertexModel
from kivent_noise.noise import scaled_octave_noise_2d

from colors import (
    gen_star_color_levels, gen_color_palette,
    sun_choices, color_choices,
    )
from utils import lerp_color


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
        star_names = self.generate_stars(
            1., 4., 5., sun_choices, 20, 10, 10, 20, 30
            )
        self.star_names = star_names
        self.planet_names = planet_names = {}
        planet_names['small_planets'] = self.generate_planets(
            100., 100., 100., 10, 
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
        self.redraw_map()

    def populate_model_with_noise(
        self, model_name, octaves, 
        persistence, scale, offset, radius, colors, 
        transparent_level = 0., default_alpha = 255
        ):
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
            level_choices=[1, 1, 1, 1, 1, 1, 2, 3]
            )
        self.populate_model_with_noise(
            model_name, 16, uniform(.5, .9),
            uniform(.03, .05), (uniform(radius, 10000.), 
            uniform(radius, 10000.)), radius, colors
            )

    def generate_star(
        self, model_name, sides, color, max_radius, 
        do_copy=False
        ):
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

    def generate_offset_star(
        self, model_name, sides, color, max_radius_1, 
        max_radius_2, do_copy=False
        ):
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

    def draw_planet(self, model_name, cloud_name, radius, color1, color2):
        divisions = randint(6, 12)
        even_div = 1.0 / divisions
        colors = gen_color_palette(divisions, color1, 
            color2, uniform(even_div, 2*even_div), randint(1, 4),
            level_choices=[2, 3, 4, 4, 5, 5])
        self.populate_model_with_noise(model_name, 16, uniform(.3, .7),
            uniform(.004, .009), 
            (uniform(radius, radius*4), uniform(radius, radius*4)), 
            radius, colors)
        divisions = randint(4, 6)
        even_div = 1.0 / divisions
        colors = gen_color_palette(divisions, color1, 
            color2, uniform(even_div, 2*even_div), 1,
            level_choices=[1, 2, 2, 3, 4, 5], do_alpha=True, 
            alpha_low_cutoff=uniform(.2, .5), 
            alpha_high_cutoff=uniform(.6, .9),
            alpha_range=(0, 200))
        self.populate_model_with_noise(cloud_name, 8, uniform(.2, .4),
            uniform(.001, .004), 
            (uniform(radius, radius*4), uniform(radius, radius*4)), 
            radius, colors)

    def generate_planets(
        self, starting_radius, min_s, max_s, count, model_name, model_file
        ):
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

    def generate_stars(
        self, min_radius, max_radius, max_offset_radius, color_choices,
        four_side_count, offset_count, normal_count, min_sides, max_sides
        ):
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


    def draw_map(
        self, size, offset, star_count, color1, color2, 
        star_renderer=None,
        planet_renderer=None,
        sun_renderer=None,
        do_stars=True,
        max_color1_chance=.5, max_color2_chance=.25, 
        small_p_counts=[1, 1, 2, 0, 0, 0],
        medium_small_p_counts=[1, 2, 0, 0, 0, 0], 
        medium_large_p_counts=[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
        large_p_counts=[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        small_sun_counts = [1, 0, 0, 0, 0],
        medium_small_sun_counts = [1, 0, 0, 0, 0, 0],
        medium_large_sun_counts = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        large_sun_counts = [0],
        persistence=.3,
        octaves=8,
        scale=.003,
        used_planet_names=None
        ):
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
                for planet_name in sample(choices, choice(counts)):
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
                for planet_name in sample(choices, choice(counts)):
                    if planet_name in used_planet_names:
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

    def redraw_map(self):
        color1 = choice(sun_choices)
        color2 = choice(sun_choices)
        self.draw_map((2500, 2500), (randrange(0, 50000), randrange(0, 50000)),
            randrange(1000, 3000), color1, color2, 
            star_renderer='back_stars')
        used = self.draw_map((2500, 2500), (randrange(0, 50000), 
            randrange(0, 50000)), randrange(1000, 3000), color1, color2, 
            star_renderer='mid_stars')
        used = self.draw_map((2500, 2500), (randrange(0, 50000), 
            randrange(0, 50000)), randrange(1000, 3000), color1, color2, 
            sun_renderer='sun1', used_planet_names=used,
            small_sun_counts = [1, 0, 0, 0, 0],
            medium_small_sun_counts = [1, 0, 0, 0, 0, 0],
            medium_large_sun_counts = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            large_sun_counts = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],)
        used = self.draw_map((2500, 2500), (randrange(0, 50000), 
            randrange(0, 50000)), randrange(1000, 3000), color1, color2, 
            sun_renderer='sun2', used_planet_names=used)
        used = self.draw_map((2500, 2500), (randrange(0, 50000), 
            randrange(0, 50000)),
            0, color1, color2, planet_renderer='planet1', 
            small_p_counts=[1, 1, 2, 0, 0, 0],
            medium_small_p_counts=[1, 2, 0, 0, 0, 0], 
            medium_large_p_counts=[0], 
            large_p_counts=[0],
            used_planet_names=used)
        used = self.draw_map((2500, 2500), (randrange(0, 50000), 
            randrange(0, 50000)),
            0, color1, color2, planet_renderer='planet2', 
            used_planet_names=used)
