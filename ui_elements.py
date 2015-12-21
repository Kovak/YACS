from kivy.properties import (StringProperty, ObjectProperty, ListProperty, 
    DictProperty, NumericProperty, BooleanProperty)
from kivy.uix.boxlayout import BoxLayout
from kivent_core.uix.gamescreens import GameScreen


class MainScreen(GameScreen):
    current_health = NumericProperty(100.0)
    total_health = NumericProperty(100.0)
    current_ammo = NumericProperty(0)
    total_ammo = NumericProperty(100)
    weapon_name = StringProperty('default')

class HealthBar(BoxLayout):
    current_health = NumericProperty(100.0)
    total_health = NumericProperty(100.0)
    health_percentage = NumericProperty(1.0)

    def on_current_health(self, instance, value):
        if value >= 0:
            self.health_percentage = float(value)/float(self.total_health)
        else:
            self.health_percentage = 0.

class AmmoBar(BoxLayout):
    current_ammo = NumericProperty(0)
    total_ammo = NumericProperty(100)
    weapon_name = StringProperty('default')
