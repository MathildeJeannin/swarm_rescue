from typing import List

from simple_playgrounds.agent.actuators import ActuatorDevice
from simple_playgrounds.device.communication import CommunicationDevice
from simple_playgrounds.device.device import Device
from simple_playgrounds.device.sensor import SensorDevice
from simple_playgrounds.common.definitions import ElementTypes
from simple_playgrounds.element.elements.modifier import DeviceDisabler, CommunicationDisabler, SensorDisabler

from spg_overlay.drone_sensors import DroneGPS


class NoComZone(CommunicationDisabler):
    def __init__(self, **entity_params):

        default_config = {'physical_shape': 'rectangle', 'texture': {'texture_type': 'color', 'color': [230, 0, 126]}}
        entity_params = {**default_config, **entity_params}

        super().__init__(**entity_params)


class NoGpsZone(SensorDisabler):
    def __init__(self, **entity_params):

        default_config = {'physical_shape': 'rectangle', 'texture': {'texture_type': 'color', 'color': [0, 32, 255]}}
        entity_params = {**default_config, **entity_params}

        super().__init__(disabled_sensor_types=DroneGPS, **entity_params)

