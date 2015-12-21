from kivent_core.systems.gamesystem import GameSystem
from kivy.properties import DictProperty, BooleanProperty, StringProperty
from kivy.factory import Factory


class ExplosionTemplate(object):
    def __init__(self, explosion_name, pause_time, remove_time):
        self.explosion_name = explosion_name
        self.pause_time = pause_time
        self.remove_time = pause_time + remove_time


class ExplosionSystem(GameSystem):
    updateable = BooleanProperty(True)
    do_components = BooleanProperty(True)
    system_id = StringProperty("explosions")

    def __init__(self, **kwargs):
        super(ExplosionSystem, self).__init__(**kwargs)
        self.template_register = {}

    def init_component(self, component_index, entity_id, zone, args):
        '''Override this function to provide custom logic for setting up your 
        component, by default each key, val pair of args will be setattr on 
        the component.'''
        component = self.components[component_index]
        component.entity_id = entity_id
        component.current_time = 0
        component.pause_time = args.get('pause_time')

    def update(self, dt):
        entities = self.gameworld.entities
        for component in self.components:
            if component is not None:
                entity_id = component.entity_id
                entity = entities[entity_id]
                comp = entity.explosions
                comp.current_time += dt
                if comp.current_time >= comp.pause_time:
                    entity.emitters.emitters[0].paused = True

    def register_template(self, template_name, explosion_name, pause_time, 
        remove_time):
        self.template_register[template_name] = ExplosionTemplate(
            explosion_name, pause_time, remove_time
            )

    def spawn_object_from_template(self, template_name, position, rotation=0.):
        template = self.template_register[template_name]
        create_component_dict = {
            'position': position,
            'rotate': rotation,
            'emitters': [template.explosion_name],
            'explosions': {'pause_time': template.pause_time},
            'lifespan': {'lifespan': template.remove_time},
            }
        component_order = [
            'position', 'rotate', 'emitters', 'explosions', 'lifespan',
            ]
        return self.gameworld.init_entity(
            create_component_dict, component_order,
            )

Factory.register("ExplosionSystem", cls=ExplosionSystem)