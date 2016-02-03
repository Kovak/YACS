from kivent_core.systems.gamesystem import GameSystem
from kivy.factory import Factory
from kivy.properties import (NumericProperty, BooleanProperty, ObjectProperty,
    ListProperty, StringProperty)
from kivy.clock import Clock
from kivy.vector import Vector


class PlayerSystem(GameSystem):
    current_entity = NumericProperty(None, allownone=True)
    physics_system = ObjectProperty(None)
    camera_system = ObjectProperty(None)
    touch_count = NumericProperty(0)
    current_health = NumericProperty(100.)
    total_health = NumericProperty(100.)
    current_shields = NumericProperty(0.)
    total_shields = NumericProperty(100.)
    current_weapon_name = StringProperty('Weapon Name')
    current_ammo = NumericProperty(0)
    total_ammo = NumericProperty(100)
    engine_rumble = NumericProperty(None)
    sound_manager = ObjectProperty(None)
    updateable = BooleanProperty(True)
    last_touch = ListProperty([])
    weapon_system = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(PlayerSystem, self).__init__(**kwargs)

    def set_boosting(self, dt):
        if self.current_entity is not None:
            entity = self.gameworld.entities[self.current_entity]
            ship_comp = entity.ship_system
            ship_comp.boosting = True
            if self.engine_rumble is not None:
                self.sound_manager.play_direct_loop(self.engine_rumble, 1.)


    def get_distance_from_player_scalar(self, position, max_distance=250):
        current_entity = self.current_entity
        entities = self.gameworld.entities
        if current_entity == None:
            return 0.

        entity = entities[current_entity]
        position_comp = entity.position
        distance = Vector(position_comp.pos).distance(position)
        if distance > max_distance:
            return 0.
        else:
            return 1. - distance/max_distance

    def update(self, dt):
        if self.current_entity is not None:
            entity = self.gameworld.entities[self.current_entity]
            combat_stats = entity.combat_stats
            weapon_comp = entity.projectile_weapons
            current_weapon = weapon_comp.equipped_weapon
            self.current_health = combat_stats.health
            self.current_ammo = current_weapon.in_clip
            self.total_ammo = current_weapon.ammo_count
            if hasattr(entity, 'shields'):
                shield_comp = entity.shields
                self.current_shields = shield_comp.current_health
                self.total_shields = shield_comp.max_health
            if self.last_touch != []:
                camera_system = self.camera_system
                world_pos = camera_system.convert_from_screen_to_world(
                    self.last_touch)
                steering = entity.steering
                steering.target = world_pos
                steering.active = True

    def on_touch_down(self, touch):
        touch.grab(self)
        self.touch_count += 1
        touch_radius = 20
        touch_count = self.touch_count
        physics_system = self.physics_system
        camera_system = self.camera_system
        world_pos = camera_system.convert_from_screen_to_world(touch.pos)
        x, y = world_pos
        collide_area = [
            x - touch_radius, y - touch_radius,
            x + touch_radius, y + touch_radius
            ]
        self.last_touch = []
        if self.current_entity is not None:
            entity = self.gameworld.entities[self.current_entity]
            collisions = physics_system.query_bb(collide_area)
            if len(collisions) > 0:
                weapons = entity.projectile_weapons
                weapons.firing = True
            elif touch_count == 1:
                steering = entity.steering
                steering.target = world_pos
                self.last_touch = touch.pos
                steering.active = True
                Clock.schedule_once(self.set_boosting, .5)
            elif touch_count == 2:
                weapons = entity.projectile_weapons
                weapons.firing = True
                Clock.unschedule(self.set_boosting)
            return True
        else:
            return False

    def on_touch_move(self, touch):
        if self.touch_count == 1:
            camera_system = self.camera_system
            world_pos = camera_system.convert_from_screen_to_world(touch.pos)
            if self.current_entity is not None:
                entity = self.gameworld.entities[self.current_entity]
                steering = entity.steering
                steering.target = world_pos
                self.last_touch = touch.pos


    def on_touch_up(self, touch):
        if self.current_entity is not None:
            entity = self.gameworld.entities[self.current_entity]
            ship_comp = entity.ship_system
            ship_comp.boosting = False
            if self.engine_rumble is not None:
                self.sound_manager.stop_direct(self.engine_rumble)
            self.last_touch = []

        Clock.unschedule(self.set_boosting)
        if touch.grab_current is self:
            self.touch_count -= 1
        super(PlayerSystem, self).on_touch_up(touch)

    def load_player(self):
        ship_system = self.gameworld.system_manager['ship_system']
        ship_id = ship_system.spawn_ship('ship1', True, (500., 500.))
        template = ship_system.templates['ship1']
        self.current_health = template.health
        self.total_health = template.health
        self.current_entity = ship_id
        self.current_weapon_name = self.weapon_system.get_current_weapon_name(
            ship_id)
        camera = self.gameworld.system_manager['camera_planet2']
        camera.focus_entity = True
        camera.entity_to_focus = ship_id

Factory.register('PlayerSystem', cls=PlayerSystem)