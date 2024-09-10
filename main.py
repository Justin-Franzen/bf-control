from nicegui import native, ui
from pathlib import Path
import json

CONFIG_FILE = Path.home().joinpath("bfcontrol.json")

class Lights:
    def __init__(self):
        self.brightness = 100.0
    def update_brightness(self, brightness= 10.0):
        self.brightness = brightness
        self.call_update()
    def call_update(self):
        print("update: " + str(self.brightness))
    
    value = "60.0"
    headers = {
        "Authorization": "1234",
        "Accept": "application/json"
        }
    
    url_list = ['https://192.168.1.135/api/rest/v1/protocols/bacnet/local/objects/analog-value/355210/properties/present-value',
                'https://192.168.1.135/api/rest/v1/protocols/bacnet/local/objects/analog-value/102611/properties/present-value']
    
    
    async def fetch(session, url):
        async with session.post(url,json={"value": value}, verify_ssl=False, headers=headers) as response:
            print("Status:", response.status)
            print("Content-type:", response.headers['content-type'])
    
    
    async def fetch_all(urls, loop):
        async with aiohttp.ClientSession(loop=loop) as session:
            results = await asyncio.gather(*[fetch(session, url) for url in urls], return_exceptions=True)
            return results
    

class Settings:
    def __init__(self):
        if(not CONFIG_FILE.exists()):
            self._create_config()
        with open(CONFIG_FILE.as_posix(), 'r') as openfile:
            self.config = json.load(openfile)
    
    def _create_config(self):
        config = {
            "light_ids": [1,2],
            "nlight_ip": "192.168.1.5",
            "auth_header": "SuperSecret",
            "worship_lvl": 1.0,
            "teaching_lvl": 60.0,
        }
        with open(CONFIG_FILE.as_posix(), "w") as outfile:
            outfile.write(json.dumps(config, indent=4))
        
dark = ui.dark_mode().enable()
config = Settings().config
lights = Lights()

print(config)
ui.label('Lighting Control')

with ui.button_group():
    ui.button('Off',on_click=lambda:(lights.update_brightness(0.0)))
    ui.button('On', on_click=lambda:(lights.update_brightness(100.0)))
    ui.button('Worship/Prayer', on_click=lambda:(lights.update_brightness(config["worship_lvl"])))
    ui.button('Teaching', on_click=lambda: (lights.update_brightness(config["teaching_lvl"])))

with ui.row():
    ui.label("Dimmer:")
    with ui.grid(columns='20px 200px'):
        ui.label().bind_text_from(lights, 'brightness')
        ui.slider(min=0.0, max=100.0, step=1.0).bind_value(lights, 'brightness').on('change', lambda: lights.call_update())

ui.run(port=native.find_open_port(), native=True, window_size=(400, 300), fullscreen=False, title="Bright Field Controls")
