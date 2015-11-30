from kivent_core.systems.gamesystem import GameSystem
from kivy.properties import BooleanProperty
from kivy.factory import Factory
import math
from kivent_core.memory_handlers.utils import memrange

class ShipTemplate(object):

    def __init__(self, template_name, name, model, texture, collision_type,
        health, mass, max_speed, max_turn_speed, accel, 
        angular_accel, boost_force,
        boost_drain, max_boost_speed, armor, boost_reserve,
        boost_regen, width, height, weapons, emitters,
        emitter_speed_base, scale_base, emitter_scaling_factor):
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


class ShipSystem(GameSystem):
    updateable = BooleanProperty(True)

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
        ):
        self.templates[template_name] = ShipTemplate(
            template_name, name, model, texture, collision_type, health,
            mass, max_speed, max_turn_speed, accel, 
            angular_accel, boost_force,
            boost_drain, max_boost_speed, armor, boost_reserve,
            boost_regen, width, height, weapons, emitters,
            emitter_speed_base, scale_base, emitter_scaling_factor
            )

        # ship_dicts['ship_2'] = {
        #     'name': 'Falcon','health': 150, 'mass': 175,'max_speed': 190, 
        #     'max_turn_speed': 100, 'accel': 20000,'angular_accel': 75, 
        #     'caliber': '6px', 
        #     'num_weapons': 4, 'texture': 'ship3', 'price': 1000,
        #     'width': 130, 'height': 70, 'offset_distance': 50, 
        #     'color': 'orange',
        #     'engine_effect': 'assets/pexfiles/engine_burn_effect4.pex', 
        #     'engine_offset': 30,
        #     'explosion_effect': 'assets/pexfiles/ship_explosion1.pex',
        #     'hard_points': [(38, 30), (-38, 30), (52, 30), (-52, 30)], 
        #     'total_rocket_ammo': 60, 'total_bullet_ammo': 400,
        #     'texture_size': (86, 128)}
        # ship_dicts['ship_3'] = {
        #     'name': 'Monarch','health': 165, 'mass': 220,'max_speed': 180, 
        #     'max_turn_speed': 130, 'accel': 25000,
        #     'angular_accel': 100, 'caliber': '8px', 
        #     'num_weapons': 2, 'texture': 'ship2-1', 'price': 1000,
        #     'width': 90, 'height': 104, 
        #     'offset_distance': 50, 'color': 'blue',
        #     'engine_effect': 'assets/pexfiles/engine_burn_effect2.pex', 
        #     'engine_offset': 50,
        #     'explosion_effect': 'assets/pexfiles/ship_explosion1.pex',
        #     'hard_points': [(28, 51), (-28, 51)],
        #     'total_rocket_ammo': 30, 'total_bullet_ammo': 240,
        #     'texture_size': (128, 128)}
        # ship_dicts['ship_4'] = {
        #     'name': 'Archon','health': 130, 'mass': 140,'max_speed': 200, 
        #     'max_turn_speed': 110, 'accel': 18000,'angular_accel': 50, 
        #     'caliber': '14px', 
        #     'num_weapons': 1, 'texture': 'ship5', 'price': 1000,
        #     'width': 62, 'height': 100, 
        #     'offset_distance': 50, 'color': 'orange',
        #     'engine_effect': 'assets/pexfiles/engine_burn_effect6.pex', 
        #     'engine_offset': 27,
        #     'explosion_effect': 'assets/pexfiles/ship_explosion1.pex',
        #     'hard_points': [(18, 63)], 'total_rocket_ammo': 15, 
        #     'total_bullet_ammo': 150,
        #     'texture_size': (112, 72)}
        # ship_dicts['ship_5'] = {
        #     'name': 'Cavalier','health': 110, 'mass': 120,'max_speed': 220, 
        #     'max_turn_speed': 125, 'accel': 22000,'angular_accel': 45, 
        #     'caliber': '8px', 
        #     'num_weapons': 1, 'texture': 'ship6', 'price': 1000,
        #     'width': 66, 'height': 80, 
        #     'offset_distance': 50, 'color': 'green',
        #     'engine_effect': 'assets/pexfiles/engine_burn_effect8.pex', 
        #     'engine_offset': 47,
        #     'explosion_effect': 'assets/pexfiles/ship_explosion1.pex',
        #     'hard_points': [(0, 47)], 'total_rocket_ammo': 12, 
        #     'total_bullet_ammo': 200,
        #     'texture_size': (96, 80)}
        # ship_dicts['ship_6'] = {
        #     'name': 'Shield','health': 150, 'mass': 160,'max_speed': 180, 
        #     'max_turn_speed': 150, 'accel': 25000,
        #     'angular_accel': 115, 'caliber': '6px', 
        #     'num_weapons': 2, 'texture': 'ship7', 'price': 1000,
        #     'width': 76, 'height': 80, 
        #     'offset_distance': 50, 'color': 'blue',
        #     'engine_effect': 'assets/pexfiles/engine_burn_effect9.pex', 
        #     'engine_offset': 45,
        #     'explosion_effect': 'assets/pexfiles/ship_explosion1.pex',
        #     'hard_points': [(-6, 47), (6, 47)], 'total_rocket_ammo': 30, 
        #     'total_bullet_ammo': 200,
        #     'texture_size': (96, 88)}
        
    # def get_ship_values(self, ship_name):
    #     if ship_name in self.ship_dicts:
    #         return self.ship_dicts[ship_name] 
    #     else:
    #         print 'ship: ', ship_name, 'does not exist'

    # def clear_ships(self):
    #     for entity_id in self.entity_ids:
    #         Clock.schedule_once(partial(
    #             self.gameworld.timed_remove_entity, entity_id))

    # def fire_projectiles(self, entity_id):
    #     gameworld = self.gameworld
    #     systems = gameworld.systems
    #     projectile_system = systems['projectile_system']
    #     projectile_system.add_fire_event(entity_id)



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
                if speed < 5.0:
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
            # physics_data = character.cymunk_physics
            # physics_body = physics_data.body
            # system_data = getattr(character, system_id)
            # if system_data.fire_engines and hasattr(
            #     physics_data, 'unit_vector'):   
            #     unit_vector = physics_data.unit_vector
            #     offset_distance = system_data.offset_distance
            #     offset = (offset_distance * -unit_vector[0], 
            #         offset_distance * -unit_vector[1])
            #     engine_speed_multiplier = system_data.engine_speed_multiplier
            #     accel = system_data.accel
            #     force = (engine_speed_multiplier * accel*dt * unit_vector[0], 
            #         engine_speed_multiplier * accel*dt * unit_vector[1])
            #     physics_body.apply_impulse(force, offset)

                
    # def damage(self, entity_id, damage):
    #     system_id = self.system_id
    #     entities = self.gameworld.entities
    #     entity = entities[entity_id]
    #     system_data = getattr(entity, system_id)
    #     system_data.health -= damage
    #     if system_data.health < 0:
    #         system_data.health = 0
    #     player_character_system = self.gameworld.systems['player_character']
    #     if entity_id == player_character_system.current_character_id:
    #         player_character_system.current_health = system_data.health

    # def collision_begin_ship_probe(self, space, arbiter):
    #     gameworld = self.gameworld
    #     systems = gameworld.systems
    #     entities = gameworld.entities
    #     character_id = systems['player_character'].current_character_id
    #     probe_id = arbiter.shapes[1].body.data
    #     ship_id = arbiter.shapes[0].body.data
    #     if ship_id == character_id:
    #         probe = entities[probe_id]
    #         ship = entities[ship_id]
    #         ship.ship_system.current_probes += 1
    #         sound_system = systems['sound_system']
    #         Clock.schedule_once(partial(
    #             sound_system.schedule_play, 'probepickup'))
    #         Clock.schedule_once(partial(
    #             gameworld.timed_remove_entity, probe_id))
    #         return False
    #     else:
    #         return True

    # def collision_begin_ship_asteroid(self, space, arbiter):
    #     gameworld = self.gameworld
    #     systems = gameworld.systems
    #     entities = gameworld.entities
    #     character_id = systems['player_character'].current_character_id
    #     asteroid_id = arbiter.shapes[1].body.data
    #     ship_id = arbiter.shapes[0].body.data
    #     asteroid = entities[asteroid_id]
    #     asteroid_damage = asteroid.asteroid_system.damage
    #     self.damage(ship_id, asteroid_damage)
    #     if ship_id == character_id:
    #         sound_system = systems['sound_system']
    #         Clock.schedule_once(partial(
    #             sound_system.schedule_play, 'asteroidhitship'))
    #     return True


    # def collision_object_shipview_begin(self, space, arbiter):
    #     gameworld = self.gameworld
    #     systems = gameworld.systems
    #     entities = gameworld.entities
    #     ship_id = arbiter.shapes[0].body.data
    #     object_id = arbiter.shapes[1].body.data
    #     ship_ent = entities[ship_id]
    #     in_view = ship_ent.ship_system.in_view
    #     if object_id not in in_view:
    #         in_view.append(object_id)
    #     return False

    # def collision_object_shipview_end(self, space, arbiter):
    #     gameworld = self.gameworld
    #     systems = gameworld.systems
    #     entities = gameworld.entities
    #     ship_id = arbiter.shapes[0].body.data
    #     object_id = arbiter.shapes[1].body.data
    #     ship_ent = entities[ship_id]
    #     in_view = ship_ent.ship_system.in_view
    #     if object_id in in_view:
    #         in_view.remove(object_id)
    #     return False

    # def remove_entity(self, entity_id):
    #     gameworld = self.gameworld
    #     entities = gameworld.entities
    #     entity = entities[entity_id]
    #     if hasattr(entity.ship_system, 'linked'):
    #         linked = entity.ship_system.linked
    #         for each in linked:
    #             gameworld.remove_entity(linked[each])
    #     super(ShipSystem, self).remove_entity(entity_id)






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
            }
        combat_stats = {
            'health': template.health, 
            'armor': template.armor,
        }
        steering = {
            'turn_speed': math.radians(template.max_turn_speed),
            'stability': 9000000.0,
            'max_force': template.accel,
            'speed': template.max_speed,
            'arrived_radius': 50.
        }
        create_component_dict = {
            'position': position,
            'rotate': 0.,
            'emitters': template.emitters,
            'cymunk_physics': physics_component_dict, 
            'rotate_renderer': {
                'model_key': template.model,
                'texture': template.texture,
                }, 
            'ship_system': ship_system_dict,
            'combat_stats': combat_stats,
            'steering': steering,
            'projectile_weapons': {'weapons': template.weapons}
            }
        component_order = ['position', 'rotate', 'cymunk_physics', 
            'rotate_renderer', 'ship_system', 'steering', 'emitters',
            'projectile_weapons', 'combat_stats']
        # if is_player_character:
        #     player_character_system = systems['player_character']
        #     create_component_dict['player_character'] = {}
        #     component_order.append('player_character')
        #     player_character_system.current_bullet_ammo = ship_system_dict[
        #         'current_bullet_ammo']
        #     player_character_system.current_rocket_ammo = ship_system_dict[
        #         'current_rocket_ammo']
        #     create_component_dict['ship_ai_system'] = {'is_player': True}
        # else:
        #     Clock.schedule_once(partial(
        #         systems['sound_system'].schedule_play, 'enemyshipenterarea'))
        #     create_component_dict['ship_ai_system'] = {'is_player': False}
        # //component_order.append('ship_ai_system')
        # init_entity = gameworld.init_entity
        ship_ent_id = gameworld.init_entity(
            create_component_dict, component_order, zone='ships',
            )
        return ship_ent_id


Factory.register('ShipSystem', cls=ShipSystem)