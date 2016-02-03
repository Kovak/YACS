from kivent_core.systems.gamesystem import GameSystem
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.factory import Factory
import math
from random import choice
from kivent_core.memory_handlers.utils import memrange

class ShipTemplate(object):

    def __init__(self, template_name, name, model, texture, collision_type,
        health, mass, max_speed, max_turn_speed, accel, 
        angular_accel, boost_force,
        boost_drain, max_boost_speed, armor, boost_reserve,
        boost_regen, width, height, weapons, emitters,
        emitter_speed_base, scale_base, emitter_scaling_factor,
        explosion_sound, has_shield, shield_model, shield_health,
        shield_radius, shield_timeout, shield_recharge, radar_model_name,
        radar_texture):
        self.name = name
        self.template_name = template_name
        self.collision_type = collision_type
        self.model = model
        self.texture = texture
        self.health = health
        self.armor = armor
        self.mass = mass
        self.max_speed = max_speed
        self.max_turn_speed = max_turn_speed
        self.accel = accel
        self.angular_accel = angular_accel
        self.boost_force = boost_force
        self.boost_drain = boost_drain
        self.max_boost_speed = max_boost_speed
        self.boost_reserve = boost_reserve
        self.boost_regen = boost_regen
        self.width = width
        self.height = height
        self.weapons = weapons
        self.emitters = emitters
        self.emitter_speed_base = emitter_speed_base
        self.scale_base = scale_base
        self.emitter_scaling_factor = emitter_scaling_factor
        self.explosion_sound = explosion_sound
        self.has_shield = has_shield
        self.shield_model = shield_model
        self.shield_health = shield_health
        self.shield_radius = shield_radius
        self.shield_timeout = shield_timeout
        self.shield_recharge = shield_recharge
        self.radar_model_name = radar_model_name
        self.radar_texture = radar_texture


class ShipSystem(GameSystem):
    updateable = BooleanProperty(True)
    player_system = ObjectProperty(None)
    is_clearing = BooleanProperty(False)
    explosion_system = ObjectProperty(None)
    camera_system = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ShipSystem, self).__init__(**kwargs)
        self.templates = {}

    def register_template(self, template_name, name, model, texture, 
        collision_type, health=100,
        mass=100, max_speed=150, max_turn_speed=150, accel=15000, 
        angular_accel=45, boost_force=2500.,
        boost_drain=25., max_boost_speed=225., armor=10., boost_reserve=100.,
        boost_regen=10., width=100., height=100., weapons=[], emitters=[],
        emitter_speed_base=90., scale_base=2.2, emitter_scaling_factor=150.,
        explosion_sound=-1, has_shield=False, shield_model=None,
        shield_health=100., shield_radius=100., shield_timeout=1.25,
        shield_recharge=20., radar_model_name=None, radar_texture=None
        ):
        self.templates[template_name] = ShipTemplate(
            template_name, name, model, texture, collision_type, health,
            mass, max_speed, max_turn_speed, accel, 
            angular_accel, boost_force,
            boost_drain, max_boost_speed, armor, boost_reserve,
            boost_regen, width, height, weapons, emitters,
            emitter_speed_base, scale_base, emitter_scaling_factor,
            explosion_sound, has_shield, shield_model, shield_health,
            shield_radius, shield_timeout, shield_recharge, radar_model_name,
            radar_texture
            )

    def update(self, dt):
        entities = self.gameworld.entities
        for component in self.components:
            if component is not None:
                entity = entities[component.entity_id]
                engine_emitter = entity.emitters.emitters[0]
                physics_component = entity.cymunk_physics
                body = physics_component.body
                component.current_reserve += dt * component.boost_regen
                component.current_reserve = min(
                    component.current_reserve, component.boost_reserve
                    )
                if component.boosting and component.current_reserve > 0.:
                    impulse = body.rotation_vector
                    component.current_reserve -= dt * component.boost_drain
                    boost_force = component.boost_force * dt
                    impulse = impulse[0] * boost_force, impulse[1] * boost_force
                    body.apply_impulse(impulse)
                    body.velocity_limit = component.boost_limit
                    if component.current_reserve <= 0.:
                        component.boosting = False
                else:
                    body.velocity_limit = component.velocity_limit
                speed = body.speed
                if speed < 20.0:
                    engine_emitter.paused = True
                else:
                    engine_emitter.paused = False
                    engine_emitter.speed = (
                        speed/component.emitter_scaling_factor * 
                        component.emitter_speed_base
                        )
                    engine_emitter.start_scale = (
                        speed/component.emitter_scaling_factor * 
                        component.scale_base
                        )


    def spawn_ship(self, ship_name, is_player_character, position):
        ship_id = self.load_ship(ship_name, is_player_character, position)
        entity = self.gameworld.entities[ship_id]
        emitters = entity.emitters
        emitter = emitters.emitters[0]
        emitter.emit_angle_offset = 180.
        emitter.pos_offset = (50., 0.)
        return ship_id

    def spawn_explosion(self, entity_id):
        if not self.is_clearing:
            entity = self.gameworld.entities[entity_id]
            position = entity.position
            ship_comp = entity.ship_system
            explosion_sound = ship_comp.explosion_sound
            if explosion_sound != -1:
                volume = self.player_system.get_distance_from_player_scalar(
                    entity.position.pos, max_distance=4000.)
                sound_manager = self.gameworld.sound_manager
                sound_manager.play_direct(explosion_sound, volume)
            self.explosion_system.spawn_object_from_template(
                'ship_explosion', position.pos
                )
        if entity_id == self.player_system.current_entity:
            self.player_system.current_entity = None
            self.camera_system.entity_to_focus = None

    def load_ship(self, ship_name, is_player_character, position):
        template = self.templates[ship_name]
        gameworld = self.gameworld
        box_dict = {
            'width': template.width, 
            'height': template.height,
            'mass': template.mass}
        col_shape_dict = {
            'shape_type': 'box', 'elasticity': .5, 
            'collision_type': template.collision_type,
            'shape_info': box_dict, 'friction': 1.0
            }
        physics_component_dict = { 'main_shape': 'box', 
            'velocity': (0, 0), 'position': position, 'angle': 0, 
            'angular_velocity': 0, 'mass': template.mass, 
            'vel_limit': template.max_speed, 
            'ang_vel_limit': math.radians(template.max_turn_speed), 
            'col_shapes': [col_shape_dict]}
        ship_system_dict = {
            'name': template.name,
            'scale_base': template.scale_base,
            'emitter_speed_base': template.emitter_speed_base,
            'emitter_scaling_factor': template.emitter_scaling_factor,
            'boosting': False,
            'boost_force': template.boost_force,
            'boost_reserve': template.boost_reserve,
            'boost_drain': template.boost_drain,
            'velocity_limit': template.max_speed,
            'boost_limit': template.max_boost_speed,
            'current_reserve': template.boost_reserve,
            'boost_regen': template.boost_regen,
            'explosion_sound': template.explosion_sound
            }
        combat_stats = {
            'health': template.health, 
            'armor': template.armor,
            'destruction_callback': self.spawn_explosion,
        }
        steering = {
            'turn_speed': math.radians(template.max_turn_speed),
            'stability': 9000000.0,
            'max_force': template.accel,
            'speed': template.max_speed,
            'arrived_radius': 50.
        }
        weapon_choice = choice(
            [ 'ship1_rifle', 'ship1_shotgun', 'ship1_blaster'])
        create_component_dict = {
            'position': position,
            'rotate': 0.,
            'color': (255, 0, 0, 255),
            'emitters': template.emitters,
            'cymunk_physics': physics_component_dict, 
            'rotate_renderer': {
                'model_key': template.model,
                'texture': template.texture,
                }, 
            'ship_system': ship_system_dict,
            'combat_stats': combat_stats,
            'steering': steering,
            'projectile_weapons': {'weapons': [weapon_choice]}
            }
        component_order = ['position', 'rotate', 'color', 'cymunk_physics', 
            'rotate_renderer', 'ship_system', 'steering', 'emitters',
            'projectile_weapons', 'combat_stats']
        if not is_player_character:
            component_order.extend(['steering_ai', 'weapon_ai'])
            create_component_dict['steering_ai'] = {
                'target': self.player_system.current_entity,
                }
            create_component_dict['weapon_ai'] = {
                'line_of_sight': 600.,
                'active': True,
                'target_id': self.player_system.current_entity
                }
        if template.has_shield:
            component_order.extend(['shields', 'shield_renderer'])
            create_component_dict['shields'] = {
                'radius': template.shield_radius,
                'recharge_rate': template.shield_recharge,
                'health': template.shield_health,
                'timeout': template.shield_timeout
                }
            create_component_dict['shield_renderer'] = {
                'model_key': template.shield_model,
                'render': True
                }
        if template.radar_model_name is not None:
            component_order.extend(['radar_color', 'radar_renderer'])
            create_component_dict['radar_color'] = (255, 0, 0, 255)
            create_component_dict['radar_renderer'] = {
                'model_key': template.radar_model_name,
                'texture': template.radar_texture
                }
        ship_ent_id = gameworld.init_entity( 
            create_component_dict, component_order, zone='ships',
            )
        return ship_ent_id


Factory.register('ShipSystem', cls=ShipSystem)