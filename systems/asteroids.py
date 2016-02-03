from kivent_core.systems.gamesystem import GameSystem
from kivy.properties import BooleanProperty, StringProperty, ObjectProperty
from kivy.factory import Factory
import math

class AsteroidTemplate(object):

    def __init__(self, collision_type, max_velocity, max_angular_velocity,
        mass, radius, texture, model_key, health, armor, ship_collision_sound,
        asteroid_collision_sound, radar_model, radar_texture):
        self.collision_type = collision_type
        self.max_velocity = max_velocity
        self.max_angular_velocity = max_angular_velocity
        self.mass = mass
        self.radius = radius
        self.texture = texture
        self.model_key = model_key
        self.health = health
        self.armor = armor
        self.ship_collision_sound = ship_collision_sound
        self.asteroid_collision_sound = asteroid_collision_sound
        self.radar_model_key = radar_model
        self.radar_texture = radar_texture

class AsteroidSystem(GameSystem):
    updateable = BooleanProperty(False)
    do_components = BooleanProperty(True)
    system_id = StringProperty("asteroids")
    explosion_system = ObjectProperty(None)
    player_system = ObjectProperty(None)
    is_clearing = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(AsteroidSystem, self).__init__(**kwargs)
        self.template_register = {}


    def register_template(self, template_name, collision_type, 
        max_velocity=250., max_angular_velocity=math.radians(200.), mass=50.,
        radius=30., texture=None, model_key=None, health=15., armor=2.,
        ship_collision_sound=-1, asteroid_collision_sound=-1, radar_model=None,
        radar_texture=None):
        self.template_register[template_name] = AsteroidTemplate(
            collision_type, max_velocity, max_angular_velocity, mass, radius,
            texture, model_key, health, armor, ship_collision_sound,
            asteroid_collision_sound, radar_model, radar_texture
            )

    def spawn_explosion(self, entity_id):
        if not self.is_clearing:
            position = self.gameworld.entities[entity_id].position
            self.explosion_system.spawn_object_from_template(
                'asteroid_explosion', position.pos
                )

    def on_collision_begin_asteroid_ship(self, space, arbiter):
        asteroid_id = arbiter.shapes[0].body.data
        ship_id = arbiter.shapes[1].body.data
        entities = self.gameworld.entities
        asteroid_entity = entities[asteroid_id]
        #ship_entity = entities[ship_id]
        ship_collision_sound = asteroid_entity.asteroids.ship_collision_sound
        if ship_collision_sound != -1:
            volume_scale = self.player_system.get_distance_from_player_scalar(
                asteroid_entity.position.pos, max_distance=250.)
            self.gameworld.sound_manager.play_direct(ship_collision_sound,
                volume_scale)
        return True

    def on_collision_begin_asteroid_asteroid(self, space, arbiter):
        asteroid_id = arbiter.shapes[0].body.data
        asteroid2_id = arbiter.shapes[1].body.data
        entities = self.gameworld.entities
        asteroid_entity = entities[asteroid_id]
        #ship_entity = entities[ship_id]
        asteroid_comp = asteroid_entity.asteroids
        asteroid_collision_sound = asteroid_comp.asteroid_collision_sound
        if asteroid_collision_sound != -1:
            volume_scale = self.player_system.get_distance_from_player_scalar(
                asteroid_entity.position.pos, max_distance=250.)
            self.gameworld.sound_manager.play_direct(
                asteroid_collision_sound, volume_scale)
        return True

    def spawn_object_from_template(self, template_name, position, rotation=0.,
        velocity=(0., 0.), angular_velocity=0.):
        template = self.template_register[template_name]
        shape_dict = {
            'inner_radius': 0, 'outer_radius': template.radius, 
            'mass': template.mass, 'offset': (0, 0)
            }
        col_shape = {
            'shape_type': 'circle', 'elasticity': .5, 
            'collision_type': template.collision_type, 
            'shape_info': shape_dict, 'friction': 1.0
            }
        col_shapes = [col_shape]
        physics_component = {
            'main_shape': 'circle', 
            'velocity': velocity, 
            'position': position, 'angle': rotation, 
            'angular_velocity': angular_velocity, 
            'vel_limit': template.max_velocity, 
            'ang_vel_limit': template.max_angular_velocity, 
            'mass': template.mass, 'col_shapes': col_shapes
            }
        combat_stats_component = {
            'health': template.health, 'armor': template.armor,
            'destruction_callback': self.spawn_explosion,
            }
        create_component_dict = {
            'cymunk_physics': physics_component, 
            'rotate_renderer': {
                'texture': template.texture, 'model_key': template.model_key,
                }, 
            'position': position,
            'rotate': rotation,
            'radar_color': (150, 120, 120, 255),
            'radar_renderer': {'model_key': template.radar_model_key,
                               'texture': template.radar_texture},
            'combat_stats': combat_stats_component,
            'asteroids': {
                'ship_collision_sound': template.ship_collision_sound,
                'asteroid_collision_sound': template.asteroid_collision_sound,
                'max_damage': 40.,
                'speed_mag': 1000.,
                }
            }
        component_order = [
            'position', 'rotate', 'cymunk_physics', 'rotate_renderer', 
            'combat_stats', 'asteroids', 'radar_color', 'radar_renderer'
            ]
        return self.gameworld.init_entity(
            create_component_dict, component_order
            )

Factory.register("AsteroidSystem", cls=AsteroidSystem)