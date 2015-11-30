import os
os.environ["KIVY_AUDIO"] = "sdl2"
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivent_core.systems.gamesystem import GameSystem
from kivent_polygen.polygen_renderers import ColorPolyRenderer
from kivy.properties import StringProperty, NumericProperty
from background_generator import BackgroundGenerator
from kivent_core.managers.resource_managers import texture_manager
from utils import get_asset_path
import kivent_particles
import kivent_cymunk
import kivent_projectiles
import ships
from math import radians
import player
import explosions
import asteroids
from random import randrange


class YACSGame(Widget):
    player_entity = NumericProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super(YACSGame, self).__init__(**kwargs)
        self.gameworld.init_gameworld(
            ['back_stars', 'mid_stars', 'position', 'sun1', 'sun2',
            'camera_stars1', 'camera_stars2', 'map', 'planet1', 'planet2',
            'camera_sun1', 'camera_sun2', 'camera_planet1', 'camera_planet2',
            'scale', 'rotate', 'color', 'particles', 'emitters',
            'particle_renderer', 'cymunk_physics', 'steering', 'ship_system',
            'projectiles', 'projectile_weapons', 'lifespan', 'combat_stats',
            'asteroids'],
            callback=self.init_game
            )
        self.background_generator = BackgroundGenerator(self.gameworld)
            
    def init_game(self):
        self.setup_states()
        self.load_assets()
        self.set_state()
        self.background_generator.generate()
        self.ids.player.load_player()
        self.spawn_some_asteroids()

    def spawn_some_asteroids(self):
        asteroid_system = self.ids.asteroids

        for x in range(100):
            x = randrange(0, 2000)
            y = randrange(0, 2000)
            asteroid_system.spawn_object_from_template(
                'asteroid1', (x, y)
                )


    def load_ships(self, ship_collision_type):
        ship_system = self.ids.ship_system
        emitter_system = self.ids.emitter
        physics_system = self.ids.physics
        model_manager = self.gameworld.model_manager
        texture_name = texture_manager.load_image(
            get_asset_path('assets', 'ships', 'ship1.png')
            )
        model_name = model_manager.load_textured_rectangle(
            'vertex_format_4f', 104, 128, 'ship1', '4f_ship1',
            )
        effect_name = emitter_system.load_effect(
            get_asset_path('assets', 'vfx', 'engine1.kep')
            )
        ship_system.register_template(
            'ship1', 'Bulldog', model_name, 
            'ship1', ship_collision_type, health=180., mass=250.,
            max_speed=150., max_turn_speed=150., accel=15000.,
            angular_accel=45.,
            boost_force=25000., boost_drain=25., max_boost_speed=225.,
            armor=10., boost_reserve=50., boost_regen=10., width=96.,
            height=108., weapons=['test_weapon'], emitters=[effect_name], 
            emitter_speed_base=90.,
            scale_base=2.2, emitter_scaling_factor=150.,
            )
                

    def load_assets(self):
        model_manager = self.gameworld.model_manager
        emitter_system = self.ids.emitter
        projectile_system = self.ids.projectiles
        weapon_system = self.ids.weapons
        sound_manager = self.gameworld.sound_manager
        asteroid_system = self.ids.asteroids
        physics_system = self.ids.physics
        explosion_system = self.ids.explosions
        texture_manager.load_atlas(
            get_asset_path('assets', 'particles', 'particles.atlas')
            )
        texture_manager.load_image(
            get_asset_path('assets', 'objects', 'asteroid1.png')
            )
        texture_manager.load_image(
            get_asset_path('assets', 'particles', 'particle3.png')
            )
        texture_manager.load_image(
            get_asset_path('assets', 'projectiles', 'bullet-14px.png')
            )

        bullet_model = model_manager.load_textured_rectangle(
            'vertex_format_4f', 14, 14, 'bullet-14px', '4f_test_bullet')
        asteroid_model = model_manager.load_textured_rectangle(
            'vertex_format_4f', 64, 64, 'asteroid1', '4f_asteroid1',
            )
        asteroid_collision_type = physics_system.register_collision_type(
            'asteroids'
            )
        projectile_system.add_origin_collision_type(asteroid_collision_type)
        ship_hit_asteroid = sound_manager.load_sound(
            'ship_hit_asteroid',
            get_asset_path('assets', 'soundfx', 'shiphit.wav')
            )
        asteroid_hit_asteroid = sound_manager.load_sound(
            'asteroid_hit_asteroid',
            get_asset_path('assets', 'soundfx', 'asteroidhitasteroid.wav')
            )
        asteroid_system.register_template(
            'asteroid1', asteroid_collision_type, 
            mass=50., radius=30., texture='asteroid1',
            model_key=asteroid_model, health=2., armor=0.,
            ship_collision_sound = ship_hit_asteroid,
            asteroid_collision_sound = asteroid_hit_asteroid,
            )

        emitter_system.load_effect(
            get_asset_path('assets', 'vfx', 'energy_projectile_1.kep')
            )
        emitter_system.load_effect(
            get_asset_path('assets', 'vfx', 'asteroidexplosion.kep')
            )
        hit_sound = sound_manager.load_sound('hitsound1',
            get_asset_path('assets', 'soundfx', 'energyhit.wav'))
        print(hit_sound, 'lazer sound')
        bullet_type = projectile_system.register_projectile_template(
            'test_bullet',
            10., 1., 1, None, None, 12, 12, 100,
            550., 50., main_effect="energy_projectile_1",
            hit_sound=hit_sound
            )
        begin = sound_manager.load_sound(
            'weapon1-reload-begin', 
            get_asset_path('assets', 'soundfx', 'weapon2', 'reload-laser.wav'))
        end = sound_manager.load_sound(
            'weapon1-reload-end', 
            get_asset_path('assets', 'soundfx', 'weapon2', 'reload-end.wav'))
        fire_sound = sound_manager.load_sound(
            'weapon1-shoot', 
            get_asset_path('assets', 'soundfx', 'weapon2', 'shoot.wav')
            )
        weapon_system.register_weapon_template('test_weapon', 1.5,
            1, 100, .4, 12, [(46., 59.), (-46., 59.)],
            2, bullet_type, 12, 12, 50000, reload_begin_sound=begin,
            reload_end_sound=end, fire_sound=fire_sound, spread=radians(0.),
            shot_count=1, time_between_shots=0.35)
        explosion_system.register_template(
            'asteroid_explosion', 'asteroidexplosion', 1.5, 1.0)
        ship_collision_type = physics_system.register_collision_type(
            'ships'
            )
        physics_system.add_collision_handler(
            asteroid_collision_type, ship_collision_type,
            begin_func=asteroid_system.on_collision_begin_asteroid_ship)
        physics_system.add_collision_handler(
            asteroid_collision_type, asteroid_collision_type,
            begin_func=asteroid_system.on_collision_begin_asteroid_asteroid)
        self.load_ships(ship_collision_type)

    def update(self, dt):
        self.gameworld.update(dt)

    def reload(self):
        self.background_generator.redraw_map()
        self.ids.player.load_player()
        self.spawn_some_asteroids()

    def clear(self):
        camera = self.ids.camera_top
        camera.focus_entity = False
        self.ids.player.current_entity = None
        self.ids.asteroids.is_clearing = True
        self.gameworld.clear_entities()
        self.ids.asteroids.is_clearing = False

    def setup_states(self):
        self.gameworld.add_state(
            state_name='main', 
            systems_added=[
                'back_stars', 'mid_stars', 'sun1', 'sun2',
                'planet1', 'planet2', 'particle_renderer', 'rotate_renderer',
                ],
            systems_removed=[], systems_paused=[],
            systems_unpaused=[
                'back_stars', 'mid_stars', 'sun1', 'sun2',
                'planet1', 'planet2', 'emitters', 'particles',
                'particle_renderer', 'steering', 'cymunk_physics',
                'rotate_renderer', 'projectiles', 'projectile_weapons',
                'lifespan', 'combat_stats',
                ],
            screenmanager_screen='main'
            )

    def set_state(self):
        self.gameworld.state = 'main'

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
