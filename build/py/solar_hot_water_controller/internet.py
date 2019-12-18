from lib.esp8266.wemos.d1mini import status_led
from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.sensors.temperature import TemperatureSensor
from lib.home_assistant.climate import Climate, MODE_AUTO, MODE_OFF
from lib.home_assistant_mqtt import HomeAssistantMQTT
from micropython import schedule
import config
import secrets
import wifi

wifi.disable_access_point()
wifi.connect(secrets.WIFI_NAME, secrets.WIFI_PASSWORD)

class Internet():
    def __init__(self, state):
        print(HomeAssistant.UID)

        HomeAssistant.NAME = config.NAME
        HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

        self.ha = ha = HomeAssistantMQTT(secrets)

        solar_temperature_sensor = ha.register('Solar', TemperatureSensor)
        tank_temperature_sensor = ha.register('Tank', TemperatureSensor)
        
        controller = ha.register(
            'Controller',
            Climate,
            initial = config.TANK_TARGET_TEMPERATURE,
            max = 90
        )
        
        def controller_mode_command(message):
            state.set(mode = message.decode('utf-8'))

        ha.subscribe(controller.mode_command_topic(), controller_mode_command)

        def controller_temperature_command(message):
            state.set(tank_target_temperature = round(float(message)))

        ha.subscribe(controller.temperature_command_topic(), controller_temperature_command)

        if wifi.is_connected():
            ha.mqtt_connect()

        ## Prevent publishing config in the future because it will fail with out-of-memory error:
        ha.publish_config_on_connect = False

        state.set(
            mode = MODE_AUTO,
            tank_target_temperature = config.TANK_TARGET_TEMPERATURE,
        )
        
        self.publish_scheduled = False

        def publish_state(_):
            self.publish_scheduled = False
            solar_temperature_sensor.set_state(state.solar_temperature)
            tank_temperature_sensor.set_state(state.tank_temperature)
            controller.set_current_temperature(state.tank_temperature)
            controller.set_action("off" if state.mode == MODE_OFF else ("heating" if state.pump else "idle"))
            state.set(
                telemetry = ha.publish_state()
            )

        self.publish_state = publish_state

    def on_state_change(self, state, changed):
        if not self.publish_scheduled:
            self.publish_scheduled = True
            schedule(self.publish_state, None)

    def wait_for_messages(self):
        self.ha.wait_for_messages(
            status_led = status_led,
            connection_required = False
        )
