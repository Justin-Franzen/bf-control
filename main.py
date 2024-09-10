from nicegui import native, ui
from pathlib import Path
import configparser

_config_file_ = Path.home().joinpath("bfcontrol.toml")

class Lights:
    def __init__(self):
        self.brightness = 100.0
    def update_brightness(self, brightness= 10.0):
        self.brightness = brightness
        self.call_update()
    def call_update(self):
        print("update: " + str(self.brightness))

class Settings:
    def __init__(self):
        if(not _config_file_.exists()):
            self._create_config()
        config = configparser.ConfigParser()
        config.sections()
        self.config = config.read(_config_file_.as_posix())
    def _create_config(self):
        config = configparser.ConfigParser()
        config["light_ids"] =[1,2]
        config["nlight_ip"] ="192.168.1.5"
        config["auth_header"]= "SuperSecret"
        
dark = ui.dark_mode().enable()
config = Settings().config
lights = Lights()

ui.label('Lighting Control')

with ui.button_group():
    ui.button('Off',on_click=lambda:(lights.update_brightness(0.0)))
    ui.button('On', on_click=lambda:(lights.update_brightness(100.0)))
    ui.button('Worship/Prayer', on_click=lambda:(lights.update_brightness(1.0)))
    ui.button('Teaching', on_click=lambda: (lights.update_brightness(60.0)))

with ui.row():
    ui.label("Dimmer:")
    with ui.grid(columns='20px 200px'):
        ui.label().bind_text_from(lights, 'brightness')
        ui.slider(min=0.0, max=100.0, step=1.0).bind_value(lights, 'brightness').on('change', lambda: lights.call_update())

ui.run(port=native.find_open_port(), native=True, window_size=(400, 300), fullscreen=False, title="Bright Field Controls")