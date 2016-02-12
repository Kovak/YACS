import os
os.environ["KIVY_AUDIO"] = "sdl2"
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivent_core.systems.gamesystem import GameSystem
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from background_generator import BackgroundGenerator, WorldSeed
from kivent_core.managers.resource_managers import texture_manager
from utils import get_asset_path
import kivent_particles
import kivent_cymunk
import kivent_projectiles
from math import radians
from systems import player, explosions, asteroids, ships, shield, globalmap
from random import randrange, randint, choice
import ui_elements
from generate_assets import generate_shield_model
from grid_generation import load_grid, generate_grid

class YACSGame(Widget):
    player_entity = NumericProperty(None, allownone=True)
    is_clearing = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(YACSGame, self).__init__(**kwargs)
        self.gameworld.init_gameworld(
            ['back_stars', 'mid_stars', 'position', 'sun1', 'sun2',
            'camera_stars1', 'camera_stars2', 'map', 'planet1', 'planet2',
            'camera_sun1', 'camera_sun2', 'camera_planet1', 'camera_planet2',
            'scale', 'rotate', 'color', 'particles', 'emitters',
            'particle_renderer', 'cymunk_physics', 'steering', 'ship_system',
            'projectiles', 'projectile_weapons', 'lifespan', 'combat_stats',
            'asteroids', 'steering_ai', 'weapon_ai', 'shields',
            'shield_renderer', 'map_grid', 'grid_camera', 'radar_renderer',
            'radar_color', 'world_grid', 'global_map', 'global_camera',
            'world_map', 'global_map_renderer'],
            callback=self.init_game
            )
        self.background_generator = BackgroundGenerator(self.gameworld)
            
    def init_game(self):
        self.world_seed = WorldSeed('kovak', (2500., 2500.))
        self.setup_states()
        self.ids.shields.register_collision()
        self.load_assets()
        global_map = self.ids.global_map
        self.set_state('main')
        self.background_generator.generate()
        self.background_generator.generate_map(self.world_seed,
                                               global_map.world_x,
                                               global_map.world_y)
        self.ids.player.load_player()
        self.load_music()
        self.setup_grid()
        global_map.setup_grid()
        global_map.setup_map_stars(self.background_generator)
        global_map.setup_zones(self.world_seed)
        self.create_minimap_grid()
        #self.load_enemy_ship()

    def increment_world_y(self, val):
        self.world_y += val

    def increment_world_x(self, val):
        self.world_x += val

    def setup_grid(self):
        outer_color = [150, 0, 100, 100]
        inner_color = [150, 0, 100, 255]
        grid_size = 17
        actual_size = (2500, 2500)
        actual_pos = (0., 0.)
        grid_offset, grid_data = generate_grid(0., 10., 1., actual_size,
                                               actual_pos, grid_size,
                                               outer_color, inner_color)
        self.grid_model = load_grid(self.gameworld, grid_data, 'mini_map_grid')
        self.grid_offset = grid_offset

    def create_minimap_grid(self):
        create_dict = {
            'position': self.grid_offset,
            'map_grid': {'model_key': self.grid_model},
            }
        ent = self.gameworld.init_entity(
            create_dict, 
            ['position', 'map_grid'])
        return ent

    def load_music(self):
        sound_manager = self.gameworld.sound_manager
        sound_manager.loop_music = True
        for x in range(1, 11):
            name = 'track' + str(x)
            track_name = sound_manager.load_music(
                name,
                get_asset_path('assets', 'music', name + '.ogg')
                )
        sound_manager.play_track(choice(sound_manager.music_dict.keys()))

    def spawn_explosion_for_blaster(self, entity_id):
        if not self.is_clearing:
            entity = self.gameworld.entities[entity_id]
            position = entity.position
            self.ids.explosions.spawn_object_from_template(
                'orb_explosion', position.pos
                )


    def load_ships(self, ship_collision_type):
        ship_system = self.ids.ship_system
        emitter_system = self.ids.emitter
        physics_system = self.ids.physics
        model_manager = self.gameworld.model_manager
        sound_manager = self.gameworld.sound_manager
        player_system = self.ids.player
        radar_texture = texture_manager.load_image(
            get_asset_path('assets', 'ships', 'ship1-radar.png'))
        texture_name = texture_manager.load_image(
            get_asset_path('assets', 'ships', 'ship1.png')
            )
        radar_model_name = model_manager.load_textured_rectangle(
            'vertex_format_4f', 104, 128, 'ship1-radar', '4f_ship1_radar')
        model_name = model_manager.load_textured_rectangle(
            'vertex_format_4f', 104, 128, 'ship1', '4f_ship1',
            )
        effect_name = emitter_system.load_effect(
            get_asset_path('assets', 'vfx', 'engine1.kep')
            )
        shield_model_data = generate_shield_model(85., 10.)
        shield_model = model_manager.load_model('vertex_format_2f4ub', 
            shield_model_data['vert_count'], shield_model_data['ind_count'],
            'shield_model', indices=shield_model_data['indices'],
            vertices=shield_model_data['vertices'], do_copy=False)


        explosion_sound = sound_manager.load_sound(
            'explosion_sound', 
            get_asset_path('assets', 'soundfx', 'explosion.wav')
            )
        ship_system.register_template(
            'ship1', 'Bulldog', model_name, 
            'ship1', ship_collision_type, health=100., mass=250.,
            max_speed=200., max_turn_speed=200., accel=15000.,
            angular_accel=45.,
            boost_force=25000., boost_drain=25., max_boost_speed=300.,
            armor=5., boost_reserve=50., boost_regen=10., width=96.,
            height=108., weapons=['ship1_shotgun'], emitters=[effect_name], 
            emitter_speed_base=90.,
            scale_base=2.2, emitter_scaling_factor=150.,
            explosion_sound=explosion_sound, has_shield=True,
            shield_model=shield_model, shield_health=100., shield_radius=90.,
            shield_timeout=1.25, shield_recharge=20.,
            radar_model_name=radar_model_name, radar_texture='ship1-radar'
            )
        ship_engine_rumble = sound_manager.load_sound(
            'engine_rumble',
            get_asset_path('assets', 'soundfx', 'shipengine.wav'),
            )
        # player_system.engine_rumble = ship_engine_rumble

    def load_weapons(self):
        emitter_system = self.ids.emitter
        projectile_system = self.ids.projectiles
        sound_manager = self.gameworld.sound_manager
        weapon_system = self.ids.weapons
        model_manager = self.gameworld.model_manager
        explosion_system = self.ids.explosions
        emitter_system.load_effect(
            get_asset_path('assets', 'vfx', 'blaster_projectile.kep')
            )
        blaster_hit_sound = sound_manager.load_sound(
            'blaster_hit',
            get_asset_path('assets', 'soundfx', 'blaster', 'hit.wav'),
            track_count=2
            )
        blaster_bullet_type = projectile_system.register_projectile_template(
            'blaster_projectile',
            10., 1., 1, None, None, 12, 12, 1.,
            550., 50., main_effect="blaster_projectile",
            hit_sound=blaster_hit_sound,
            destruction_callback=self.spawn_explosion_for_blaster
            )
        blaster_begin = sound_manager.load_sound(
            'blaster-reload-begin', 
            get_asset_path('assets', 'soundfx', 'blaster', 'reload-laser.wav'),
            track_count=2
            )
        blaster_end = sound_manager.load_sound(
            'blaster-reload-end', 
            get_asset_path('assets', 'soundfx', 'blaster', 'reload-end.wav'),
            track_count=2
            )
        blaster_fire_sound = sound_manager.load_sound(
            'blaster-shoot', 
            get_asset_path('assets', 'soundfx', 'blaster', 'shoot.wav'),
            track_count=2
            )
        emitter_system.load_effect(
            get_asset_path('assets', 'vfx', 'orb_explosion.kep')
            )
        explosion_system.register_template(
            'orb_explosion', 'orb_explosion', .3, .6)

        weapon_system.register_weapon_template(
            'ship1_blaster', 'Blaster',
            reload_time=3.5,
            projectile_type=1,
            ammo_count=100,
            rate_of_fire=.4, 
            clip_size=14,
            barrel_offsets=[(46., 59.), (-46., 59.)],
            barrel_count=2,
            ammo_type=blaster_bullet_type,
            projectile_width=12.,
            projectile_height=12.,
            accel=500,
            reload_begin_sound=blaster_begin,
            reload_end_sound=blaster_end,
            fire_sound=blaster_fire_sound,
            spread=radians(0.),
            shot_count=1,
            time_between_shots=0.35,
            )
        rifle_hit_sound = sound_manager.load_sound(
            'blaster_hit',
            get_asset_path('assets', 'soundfx', 'rifle', 'hit.wav'),
            track_count=2
            )

        bullet_tex = texture_manager.load_image(
            get_asset_path('assets', 'projectiles', 'bullet-14px.png')
            )
        bullet_model = model_manager.load_textured_rectangle(
            'vertex_format_4f', 28., 14., 'bullet-14px', '4f_bullet-14px')
        rifle_bullet_type = projectile_system.register_projectile_template(
            'rifle_projectile',
            12., 1., 1, 'bullet-14px', bullet_model, 14., 14., 10,
            750., 50.,
            hit_sound=rifle_hit_sound
            )

        rifle_begin = sound_manager.load_sound(
            'rifle-reload-begin', 
            get_asset_path('assets', 'soundfx', 'rifle', 'reload-begin.wav'),
            track_count=2
            )
        rifle_end = sound_manager.load_sound(
            'rifle-reload-end',
            get_asset_path('assets', 'soundfx', 'rifle', 'reload-end.wav'),
            track_count=2
            )
        rifle_fire_sound = sound_manager.load_sound(
            'rifle-shoot', 
            get_asset_path('assets', 'soundfx', 'rifle', 'shoot.wav'),
            track_count=2
            )
        weapon_system.register_weapon_template(
            'ship1_rifle', 'Rifle',
            reload_time=5.0,
            projectile_type=3,
            ammo_count=100,
            rate_of_fire=.5, 
            clip_size=8,
            barrel_offsets=[(46., 59.), (-46., 59.)],
            barrel_count=2,
            ammo_type=rifle_bullet_type,
            projectile_width=12.,
            projectile_height=12.,
            accel=10000.,
            reload_begin_sound=rifle_begin,
            reload_end_sound=rifle_end,
            fire_sound=rifle_fire_sound,
            spread=radians(0.),
            shot_count=2,
            time_between_shots=.1,
            )

        shotgun_begin = sound_manager.load_sound(
            'shotgun-reload-begin', 
            get_asset_path('assets', 'soundfx', 'shotgun', 'reload-begin.wav')
            )
        shotgun_end = sound_manager.load_sound(
            'shotgun-reload-end', 
            get_asset_path('assets', 'soundfx', 'shotgun', 'reload-end.wav')
            )
        shotgun_fire_sound = sound_manager.load_sound(
            'shotgun-shoot', 
            get_asset_path('assets', 'soundfx', 'shotgun', 'shoot.wav')
            )

        shotgun_bullet_tex = texture_manager.load_image(
            get_asset_path('assets', 'projectiles', 'bullet-6px.png')
            )
        shotgun_bullet_model = model_manager.load_textured_rectangle(
            'vertex_format_4f', 6., 6., 'bullet-6px', '4f_bullet-6px')
        shotgun_bullet_type = projectile_system.register_projectile_template(
            'shotgun_projectile',
            7., 1., 1, 'bullet-6px', shotgun_bullet_model, 4.5, 4.5, 2.5,
            750., 50.,
            lifespan=2.0,
            hit_sound=rifle_hit_sound
            )
        weapon_system.register_weapon_template(
            'ship1_shotgun', 'Shotgun',
            reload_time=2.5,
            projectile_type=1,
            ammo_count=100,
            rate_of_fire=.70, 
            clip_size=8,
            barrel_offsets=[(46., 59.), (-46., 59.)],
            barrel_count=2,
            ammo_type=shotgun_bullet_type,
            projectile_width=4.,
            projectile_height=4.,
            accel=3000,
            reload_begin_sound=shotgun_begin,
            reload_end_sound=shotgun_end,
            fire_sound=shotgun_fire_sound,
            spread=radians(15.),
            shot_count=5,
            time_between_shots=0.,
            )

    def load_assets(self):
        model_manager = self.gameworld.model_manager
        emitter_system = self.ids.emitter
        projectile_system = self.ids.projectiles
        weapon_system = self.ids.weapons
        sound_manager = self.gameworld.sound_manager
        asteroid_system = self.ids.asteroids
        physics_system = self.ids.physics
        shield_system = self.ids.shields
        explosion_system = self.ids.explosions
        texture_manager.load_atlas(
            get_asset_path('assets', 'particles', 'particles.atlas')
            )
        texture_manager.load_image(
            get_asset_path('assets', 'objects', 'asteroid1.png')
            )
        texture_manager.load_image(
            get_asset_path('assets', 'objects', 'asteroid1-radar.png')
            )
        texture_manager.load_image(
            get_asset_path('assets', 'particles', 'particle3.png')
            )

        asteroid_model = model_manager.load_textured_rectangle(
            'vertex_format_4f', 64, 64, 'asteroid1', '4f_asteroid1',
            )
        asteroid_radar_model = model_manager.load_textured_rectangle(
            'vertex_format_4f', 64, 64, 'asteroid1-radar', '4f_asteroid1_radar',
            )
        asteroid_collision_type = physics_system.register_collision_type(
            'asteroids'
            )
        ship_collision_type = physics_system.register_collision_type(
            'ships'
            )
        projectile_system.add_origin_collision_type(asteroid_collision_type)
        projectile_system.add_origin_collision_type(ship_collision_type)
        self.load_weapons()

        ship_hit_asteroid = sound_manager.load_sound(
            'ship_hit_asteroid',
            get_asset_path('assets', 'soundfx', 'shiphit.wav'),
            track_count=2
            )
        asteroid_hit_asteroid = sound_manager.load_sound(
            'asteroid_hit_asteroid',
            get_asset_path('assets', 'soundfx', 'asteroidhitasteroid.wav'),
            track_count=2
            )
        emitter_system.load_effect(
            get_asset_path('assets', 'vfx', 'asteroidexplosion.kep')
            )
        emitter_system.load_effect(
            get_asset_path('assets', 'vfx', 'shipexplosion.kep')
            )
        explosion_system.register_template(
            'ship_explosion', 'shipexplosion', 3.0, 1.5)
        asteroid_system.register_template(
            'asteroid1', asteroid_collision_type, 
            mass=125., radius=30., texture='asteroid1',
            model_key=asteroid_model, health=15., armor=4.,
            ship_collision_sound = ship_hit_asteroid,
            asteroid_collision_sound = asteroid_hit_asteroid,
            radar_model=asteroid_radar_model, radar_texture='asteroid1-radar'
            )

        explosion_system.register_template(
            'asteroid_explosion', 'asteroidexplosion', 1.5, 1.0)
        physics_system.add_collision_handler(
            asteroid_collision_type, ship_collision_type,
            begin_func=asteroid_system.on_collision_begin_asteroid_ship)
        physics_system.add_collision_handler(
            asteroid_collision_type, asteroid_collision_type,
            begin_func=asteroid_system.on_collision_begin_asteroid_asteroid)
        physics_system.add_collision_handler(
            asteroid_collision_type, shield_system.shield_collision_type,
            begin_func=shield_system.on_collision_begin_asteroid_shield)
        physics_system.add_collision_handler(
            shield_system.shield_collision_type,
            shield_system.shield_collision_type,
            begin_func=shield_system.on_collision_begin_shield_shield)
        physics_system.add_collision_handler(
            ship_collision_type,
            shield_system.shield_collision_type,
            begin_func=shield_system.on_collision_begin_ship_shield)
        projectile_system.add_custom_collision_type(
            shield_system.shield_collision_type,
            shield_system.on_collision_begin_bullet_shield)
        self.load_ships(ship_collision_type)


    def reload(self):
        print(self.world_x, self.world_y)
        self.create_minimap_grid()
        self.background_generator.generate_map(self.world_seed, self.world_x,
                                               self.world_y)
        self.ids.player.load_player()
        self.load_enemy_ship()

    def load_enemy_ship(self):
        ship_system = self.gameworld.system_manager['ship_system']
        ship_id = ship_system.spawn_ship('ship1', False, (1600, 1600.))

    def clear(self):
        camera = self.ids.camera_top
        camera.focus_entity = False
        self.ids.player.current_entity = None
        self.ids.asteroids.is_clearing = True
        self.ids.ship_system.is_clearing = True
        self.is_clearing = True
        self.gameworld.clear_entities()
        self.ids.asteroids.is_clearing = False
        self.ids.ship_system.is_clearing = False
        self.is_clearing = False

    def setup_states(self):
        self.gameworld.add_state(
            state_name='main', 
            systems_added=['player', 'back_stars', 'mid_stars', 'sun1', 'sun2',
                           'planet1', 'particle_renderer',
                           'rotate_renderer', 'shield_renderer', 'planet2', ],
            systems_removed=['grid_camera', 'map_grid', 'radar_renderer',
                             'world_grid', 'global_camera',
                             'global_map_renderer'],
            systems_paused=['grid_camera', 'map_grid', 'radar_renderer',
                            'global_map_renderer'],
            systems_unpaused=['back_stars', 'mid_stars', 'sun1', 'sun2',
                              'planet1', 'planet2', 'emitters', 'particles',
                              'particle_renderer', 'steering',
                              'cymunk_physics', 'rotate_renderer',
                              'projectiles', 'projectile_weapons', 'lifespan',
                              'combat_stats', 'steering_ai', 'weapon_ai',],
            screenmanager_screen='main'
            )
        self.gameworld.add_state(
            state_name='minimap', 
            systems_added=['back_stars', 'mid_stars', 'sun1', 'sun2',
                           'planet1', 'planet2', 'particle_renderer',
                           'rotate_renderer', 'shield_renderer', 'grid_camera',
                           'map_grid', 'radar_renderer'],
            systems_removed=['player', 'world_grid', 'global_camera',
                             'global_map_renderer'],
            systems_paused=['emitters', 'particles', 'steering',
                            'cymunk_physics', 'lifespan', 'projectiles',
                            'projectile_weapons',
                            'combat_stats', 'steering_ai', 'weapon_ai',
                            'global_map_renderer'],
            systems_unpaused=['back_stars', 'mid_stars', 'sun1', 'sun2',
                              'planet1', 'planet2','grid_camera', 'map_grid',
                              'radar_renderer', 'rotate_renderer',],
            screenmanager_screen='map'
            )
        self.gameworld.add_state(
            state_name='worldmap', 
            systems_added=['global_camera', 'global_map_renderer',
                           'world_grid'],
            systems_removed=['player','back_stars', 'mid_stars', 'sun1',
                             'sun2', 'planet1', 'planet2', 'particle_renderer',
                             'rotate_renderer', 'shield_renderer',
                             'grid_camera', 'map_grid', 'radar_renderer',],
            systems_paused=['emitters', 'particles',
                            'particle_renderer', 'steering', 'cymunk_physics',
                            'lifespan', 'projectiles', 'projectile_weapons',
                            'combat_stats', 'steering_ai', 'weapon_ai',
                            'back_stars', 'mid_stars', 'sun1', 'sun2',
                            'planet1', 'planet2','grid_camera', 'map_grid',
                            'radar_renderer', 'rotate_renderer'],
            systems_unpaused=['global_map_renderer'],
            on_change_callback=self.load_global_map,
            screenmanager_screen='jump'
            )

    def load_global_map(self, current_state, previous_state):
        self.ids.global_map.draw_map(self.world_seed)


    def set_state(self, state):
        self.gameworld.state = state

class DebugPanel(Widget):
    fps = StringProperty(None)

    def __init__(self, **kwargs):
        super(DebugPanel, self).__init__(**kwargs)
        Clock.schedule_once(self.update_fps)

    def update_fps(self,dt):
        self.fps = str(int(Clock.get_fps()))
        Clock.schedule_once(self.update_fps, .001)

class YACSApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1.)


if __name__ == '__main__':
    YACSApp().run()
