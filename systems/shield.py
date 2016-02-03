from kivent_core.systems.gamesystem import GameSystem
from kivy.properties import (DictProperty, BooleanProperty, StringProperty,
                            ObjectProperty, NumericProperty)
from kivy.factory import Factory
from cymunk import Circle

# class ShieldTemplate(object):
#     def __init__(self, explosion_name, pause_time, remove_time):
#         self.explosion_name = explosion_name
#         self.pause_time = pause_time
#         self.remove_time = pause_time + remove_time


class ShieldSystem(GameSystem):
    updateable = BooleanProperty(True)
    do_components = BooleanProperty(True)
    system_id = StringProperty("shields")
    physics_system = ObjectProperty(None)
    player_system = ObjectProperty(None)
    shield_collision_type = NumericProperty(None)
    combat_stats_system = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ShieldSystem, self).__init__(**kwargs)
        # self.template_register = {}

    def register_collision(self):
        physics_system = self.physics_system
        self.shield_collision_type = physics_system.register_collision_type(
            'shields')

    def on_collision_begin_ship_shield(self, space, arbiter):
        ship_id = arbiter.shapes[0].body.data
        shield_id = arbiter.shapes[1].body.data
        entities = self.gameworld.entities
        ship_entity = entities[ship_id]
        shield_entity = entities[shield_id]
        if shield_entity.shields.shield_active:
            shield_entity.shields.shield_visible = True
            return True
        else:
            return False

    def on_collision_begin_shield_shield(self, space, arbiter):
        shield1_id = arbiter.shapes[0].body.data
        shield2_id = arbiter.shapes[1].body.data
        entities = self.gameworld.entities
        shield_entity1 = entities[shield1_id]
        shield_entity2 = entities[shield2_id]
        if shield_entity1.shields.shield_active and \
           shield_entity2.shields.shield_active:
            shield_entity1.shields.shield_visible = True
            shield_entity2.shields.shield_visible = True
            print('ships collide, shields on')
            return True
        else:
            print('ships collide, shields off')
            return False

    def on_collision_begin_bullet_shield(self, space, arbiter):
        bullet_id = arbiter.shapes[0].body.data
        collision_id = arbiter.shapes[1].body.data
        entities = self.gameworld.entities
        projectile_entity = entities[bullet_id]
        shield_entity = entities[collision_id]
        comp = projectile_entity.projectiles

        shield_comp = shield_entity.shields
        if comp.origin_entity != collision_id and shield_comp.shield_active:
            damage_entity = self.combat_stats_system.damage_entity
            shield_comp.shield_visible = True
            shield_comp.current_health -= comp.damage
            shield_comp.current_timeout = shield_comp.timeout
            damage_entity(bullet_id, comp.damage, comp.armor_pierce)
            hit_sound = comp.hit_sound
            if hit_sound != -1:
                volume = self.player_system.get_distance_from_player_scalar(
                    projectile_entity.position.pos, max_distance=500.)
                sound_manager = self.gameworld.sound_manager
                sound_manager.play_direct(hit_sound, volume)
            return True
        else:
            return False

    def on_collision_begin_asteroid_shield(self, space, arbiter):
        asteroid_id = arbiter.shapes[0].body.data
        ship_id = arbiter.shapes[1].body.data
        entities = self.gameworld.entities
        asteroid_entity = entities[asteroid_id]
        ship_entity = entities[ship_id]
        asteroid_comp = asteroid_entity.asteroids
        asteroid_physics = asteroid_entity.cymunk_physics
        ship_physics = ship_entity.cymunk_physics
        asteroid_speed = asteroid_physics.body.speed
        ship_speed = ship_physics.body.speed
        ship_collision_sound = asteroid_comp.ship_collision_sound
        if ship_collision_sound != -1:
            volume_scale = self.player_system.get_distance_from_player_scalar(
                asteroid_entity.position.pos, max_distance=250.)
            self.gameworld.sound_manager.play_direct(ship_collision_sound,
                volume_scale)
        shield_comp = ship_entity.shields
        if shield_comp.shield_active:
            shield_comp.shield_visible = True
            shield_comp.current_health -= asteroid_comp.max_damage * (
                ship_speed + asteroid_speed)/asteroid_comp.speed_mag
            shield_comp.current_timeout = shield_comp.timeout
            return True
        else:
            return False

    def init_component(self, component_index, entity_id, zone, args):
        '''Override this function to provide custom logic for setting up your 
        component, by default each key, val pair of args will be setattr on 
        the component.'''
        component = self.components[component_index]
        component.entity_id = entity_id
        entity = self.gameworld.entities[entity_id]
        physics_comp = entity.cymunk_physics
        space = self.physics_system.space
        body = physics_comp.body
        new_shape = Circle(body, args.get('radius'), (0., 0.))
        new_shape.collision_type = self.shield_collision_type
        physics_comp.shapes.append(new_shape)
        space.add(new_shape)
        space.reindex_shape(new_shape)
        component.recharge_rate = args.get('recharge_rate')
        component.max_health = args.get('health')
        component.current_health = args.get('health')
        component.timeout = args.get('timeout')
        component.current_timeout = 0.
        component.shield_active = True
        component.shield_visible = False
        component.shield_broken = False
        component.shield_fade_in = .2
        component.shield_on = .5
        component.shield_fade_out = .3
        component.state = 'off'

    def update(self, dt):
        entities = self.gameworld.entities
        for component in self.components:
            if component is not None:
                entity_id = component.entity_id
                entity = entities[entity_id]
                comp = entity.shields
                color_comp = entity.color
                render_comp = entity.shield_renderer
                if comp.current_timeout > 0.:
                    comp.current_timeout -= dt
                if comp.current_timeout <= 0.:
                    comp.current_health = min(
                        comp.max_health, 
                        comp.current_health + comp.recharge_rate*dt
                        )
                    comp.shield_visible = False
                    if comp.current_health == comp.max_health:
                        comp.shield_active = True
                        comp.shield_broken = False
                if comp.current_health <= 0 and not comp.shield_broken:
                    comp.current_health = 0.
                    comp.shield_broken = True
                    comp.current_timeout = comp.timeout * 3.
                    comp.shield_visible = False
                    comp.shield_active = False
                if comp.shield_visible:
                    render_comp.render = True
                else:
                    render_comp.render = False

    # def register_template(self, template_name, explosion_name, pause_time, 
    #     remove_time):
    #     self.template_register[template_name] = ExplosionTemplate(
    #         explosion_name, pause_time, remove_time
    #         )



Factory.register("ShieldSystem", cls=ShieldSystem)