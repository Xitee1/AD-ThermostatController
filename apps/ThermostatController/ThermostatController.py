import hassapi as hass
from datetime import datetime

class ThermostatController(hass.Hass):
    """
    App to control thermostat that can be directly controlled (valve position), like the Eurotronic Spirit/Comet.
    """

    def initialize(self):
        # Init
        self.log("Initializing ThermostatController..")
        self.last_temp = 0
        self.last_executed_temp = 0
        self.last_execution_time = datetime.now()
        self.last_temp_change = datetime.now()
        self.last_valve_position = None

        # Arguments
        self.enabled = self.args['enabled']
        self.entity_thermostat = self.get_entity(self.args['entity_thermostat'])
        self.entity_valve_position = self.get_entity(self.args['entity_valve_position'])

        self.trigger_temp_diff = float(self.args['trigger_temp_diff']) if 'trigger_temp_diff' in self.args else 0.2
        self.trigger_timeout = int(self.args['trigger_timeout']) if 'trigger_timeout' in self.args else 60 * 7
        self.update_interval = int(self.args['update_interval']) if 'update_interval' in self.args else -1
        self.temp_values = self.args['temp_values'] if 'temp_values' in self.args else None
        self.valve_compare_current_value = self.args['compare_current_value'] if 'compare_current_value' in self.args else True
        self.valve_always_update = self.args['always_update'] if 'force_update' in self.args else False

        # App
        if type(self.enabled) is bool and not self.enabled:
            self.log("ThermostatController disabled.")
            return

        if self.update_interval == -1:
            self.entity_thermostat.listen_state(self.update_valve_position)
            self.entity_thermostat.listen_state(self.update_valve_position, attribute="temperature")
            self.entity_thermostat.listen_state(self.update_valve_position, attribute="current_temperature")
        else:
            self.run_every(self.update_valve_position, start=f"now+{self.update_interval}", interval=self.update_interval)
        self.log("ThermostatController initialized!")


    def update_valve_position(self, entity=None, attribute=None, old=None, new=None, kwargs=None):
        # TODO check if everything is available

        # Check if controller is enabled
        if type(self.enabled) is str and self.get_entity(self.enabled).is_state("off"):
            self.log("Controller is disabled.")
            return

        # Init values
        hvac_mode = self.entity_thermostat.get_state()
        current_temp = self.entity_thermostat.get_state(attribute="current_temperature")
        target_temp = self.entity_thermostat.get_state(attribute="temperature")
        current_time = datetime.now()
        difference_last_executed_temp = round(abs(current_temp - self.last_executed_temp), 1)

        if self.last_temp != current_temp:
            self.last_temp_change = datetime.now()
        self.last_temp = current_temp

        # Check if temperature difference is too small (only if updated by current temp change)
        #self.log(f"Attribute: {attribute} ")
        if attribute == "current_temperature":
            time_difference = (current_time - self.last_temp_change).total_seconds()
            self.log(f"Time difference: {time_difference}")
            if time_difference < self.trigger_timeout and difference_last_executed_temp < self.trigger_temp_diff:
                self.log(f"Not updating valve position (temperature difference too small. Diff to last temp: {difference_last_executed_temp}. Required diff: {self.trigger_temp_diff})")
                return

        valve_position = self.get_valve_position(target_temp, current_temp, hvac_mode)

        update_valve_same_value = True
        if not self.valve_always_update:
            if self.valve_compare_current_value:
                current_valve_position = int(self.entity_valve_position.get_state())
                self.log(f"Current valve position: {current_valve_position}")
                update_valve_same_value = valve_position != current_valve_position
            else:
                update_valve_same_value = valve_position != self.last_valve_position

        if update_valve_same_value:
            self.entity_valve_position.call_service("set_value", value=valve_position)
            self.last_valve_position = valve_position
            self.log(f"New valve position: {valve_position}")
        else:
            self.log(f"Not updating valve position (already same value ({valve_position}))")

        self.last_execution_time = current_time
        self.last_executed_temp = current_temp


    def get_valve_position(self, target_temp, current_temp, hvac_mode):
        difference = round((target_temp - current_temp), 1) # How many degrees need to be heated
        self.log(f"Valve position calculation: Temp difference: {difference}")

        if self.temp_values is None:
            self.log("Temp values are undefined!")
            return 0

        # Check if hvac mode is heat - if not, close valve.
        if hvac_mode != "heat":
            return 0

        values_len = len(self.temp_values) - 1
        for index, temp_value in enumerate(self.temp_values):
            if index == values_len:
                return int(temp_value['pos'])
            elif difference <= float(temp_value['diff']):
                return int(temp_value['pos'])

        self.log("Error while getting valve position!")
        return 0