# AD-ThermostatController

This app can control thermostats that are manually controllable like the Eurotronic Spirit or Comet.
You can specify custom values to define by with temp difference to target how much it should open the valve.


<br><br>

### Warning: This project is still under beta development! It should work but expect some bugs and that some things get changed.

<br><br>

## App configuration
### Full Example:
```yaml
ThermostatController_living_room:
  module: ThermostatController
  class: ThermostatController
  enabled: True
  entity_thermostat: climate.living_room_radiator
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

### Arguments
| key                     | required | type           | default | description                                                                                                                                                                                                                                                           |
|-------------------------|----------|----------------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `enabled`               | False    | bool or string | `True`  | Enable/Disable this instance. Value: Boolean or switch entity.                                                                                                                                                                                                        |
| `entity_thermostat`     | True     | string         |         | The entity_id of the generic_thermostat                                                                                                                                                                                                                               |
| `entity_valve_position` | True     | string         |         | The entity_id of your valve position (number or input_number)                                                                                                                                                                                                         |
| `update_interval`       | False    | int            | `-1`    | Use an fixed update interval in seconds instead updating on state change.                                                                                                                                                                                             |
| `compare_current_value` | False    | bool           | `True`  | The entity_id of your valve position (number or input_number)                                                                                                                                                                                                         |
| `force_update`          | False    | bool           | `False` | Always re-set the current valve position. Only useful if your value jumps back after some time without it being registered by HA.                                                                                                                                     |
| `temp_values`           | True     | list           |         | Define your temp and position thresholds. See example above. Please note that for the last entry you only need the pos value. It should be set to the highest position that your valve is capable of. It is used after all thresholds have been passed (max heating). |