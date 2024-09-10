from nicegui import native, ui
from pathlib import Path
import json
import asyncio
import aiohttp

CONFIG_FILE = Path.home().joinpath("bfcontrol.json")


class Lights:
    def __init__(self, config):
        self.brightness = 100.0
        self._urls = []
        self._headers = {
            "Authorization": config["auth_header"],
            "Accept": "application/json",
        }
        self._timeout = aiohttp.ClientTimeout(total=5)

        for i in config["light_ids"]:
            self._urls.append(
                "https://"
                + config["nlight_ip"]
                + "/api/rest/v1/protocols/bacnet/local/objects/analog-value/"
                + str(i)
                + "/properties/present-value"
            )

    async def update_brightness(self, brightness=10.0):
        self.brightness = brightness
        await self.update_lights()

    async def _update_post_call(self, session, url):
        async with session.post(
            url,
            json={"value": self.brightness},
            verify_ssl=False,
            headers=self._headers,
            timeout=self._timeout,
        ) as response:
            print("Status:", response.status)

    async def update_lights(
        self,
    ):
        print("update: " + str(self.brightness))
        async with aiohttp.ClientSession(loop=asyncio.get_event_loop()) as session:
            print(
                await asyncio.gather(
                    *[self._update_post_call(session, url) for url in self._urls],
                    return_exceptions=True
                )
            )


class Settings:
    def __init__(self):
        if not CONFIG_FILE.exists():
            self._create_config()
        with open(CONFIG_FILE.as_posix(), "r") as openfile:
            self.config = json.load(openfile)

    def _create_config(self):
        config = {
            "light_ids": [1, 2],
            "nlight_ip": "192.168.1.5",
            "auth_header": "SuperSecret",
            "worship_lvl": 1.0,
            "teaching_lvl": 60.0,
        }
        with open(CONFIG_FILE.as_posix(), "w") as outfile:
            outfile.write(json.dumps(config, indent=4))


dark = ui.dark_mode().enable()
config = Settings().config

lights = Lights(config)

ui.label("Lighting Control")

with ui.button_group():
    ui.button("Off", on_click=lambda: (lights.update_brightness(0.0)))
    ui.button("On", on_click=lambda: (lights.update_brightness(100.0)))
    ui.button(
        "Worship/Prayer",
        on_click=lambda: (lights.update_brightness(config["worship_lvl"])),
    )
    ui.button(
        "Teaching", on_click=lambda: (lights.update_brightness(config["teaching_lvl"]))
    )

with ui.row():
    ui.label("Dimmer:")
    with ui.grid(columns="20px 200px"):
        ui.label().bind_text_from(lights, "brightness")
        ui.slider(min=0.0, max=100.0, step=1.0).bind_value(lights, "brightness").on(
            "change", lambda: lights.update_lights()
        )

ui.run(
    port=native.find_open_port(),
    native=True,
    window_size=(400, 300),
    fullscreen=False,
    title="Bright Field Controls",
    reload=False,
)
