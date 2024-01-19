# AD-ThermostatController

This app controls thermostats that are manually controllable like the Eurotronic Spirit or Comet.
You can specify custom values to define by with temp difference to target how much it should open the valve.

<br>

### TODO:
- Error handling for missing/wrong arguments

## App configuration
### Preparing HA
First, you need to create a Home Assistant generic_thermostat entity. This is used to set the target temperature of your thermostat (You can disable the climate entity provided by the thermostat integration).
Configure everything according to your room and situation.
```yaml
# configuration.yaml
climate:
  - platform: generic_thermostat
    name: Living Room - Heater
    unique_id: living_room_heater
    heater: input_boolean.living_room_dummy_climate
    target_sensor: sensor.living_room_temperature
    min_temp: 15
    max_temp: 30
    cold_tolerance: 0.1
    hot_tolerance: 0.0
    # Optional. Define your presets & temp step.
    away_temp: 21
    comfort_temp: 24.5
    home_temp: 24.0
    sleep_temp: 23
    target_temp_step: 0.5

input_boolean:
  living_room_dummy_climate:
    name: Living room - dummy climate
```

### App (Example values)
```yaml
# appdaemon/apps.yaml
ThermostatController_living_room:
  module: ThermostatController
  class: ThermostatController
  enabled: True
  entity_thermostat: climate.living_room_heater
  entity_valve_position: number.living_room_radiator_valve_position
  update_interval: 120 # Update every 120 seconds instead listening for state changes of the climate entity.
  compare_current_value: True
  force_update: False
  temp_values:
    - diff: 0.0 # Difference between target and current temp: '0.0°'.
      pos: 0 # Pos = 0 since target has been reached.
    - diff: 0.1 # Difference '0.1°'
      pos: 20 # Little heating
    - diff: 0.5 # ... and so on
      pos: 80
    - diff: 0.7
      pos: 120
    - diff: 1.0
      pos: 160
    - diff: 1.5
      pos: 210
    - pos: 255 # All thresholds have been passed. Max heating.
```

### Parameters
| key                     | required | type           | default            | description                                                                                                                                                                                                                                                           |
|-------------------------|----------|----------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `debug`                 | False    | bool           | `False`            | Enable debug log messages.                                                                                                                                                                                                                                            |
| `enabled`               | False    | bool or string | `True`             | Enable/Disable this instance. Value: Boolean or switch entity.                                                                                                                                                                                                        |
| `entity_thermostat`     | True     | string         |                    | The entity_id of the generic_thermostat                                                                                                                                                                                                                               |
| `entity_valve_position` | True     | string         |                    | The entity_id of your valve position (number or input_number)                                                                                                                                                                                                         |
| `trigger_temp_diff`     | False    | float          | `0.2`              | Minimum required temp difference to update valve position (in order to prevent valve changing back and forth during small temp fluctuations.                                                                                                                          |
| `trigger_timeout`       | False    | int            | `60*7` (7 minutes) | Bypass `trigger_temp_diff` if the current temp did not change for this amount of time.                                                                                                                                                                                |
| `update_interval`       | False    | int            | `-1`               | Use an fixed update interval in seconds instead updating on state change.                                                                                                                                                                                             |
| `compare_current_value` | False    | bool           | `True`             | The entity_id of your valve position (number or input_number)                                                                                                                                                                                                         |
| `force_update`          | False    | bool           | `False`            | Always re-set the current valve position. Only useful if your value jumps back after some time without it being registered by HA.                                                                                                                                     |
| `temp_values`           | True     | list           |                    | Define your temp and position thresholds. See example above. Please note that for the last entry you only need the pos value. It should be set to the highest position that your valve is capable of. It is used after all thresholds have been passed (max heating). |
