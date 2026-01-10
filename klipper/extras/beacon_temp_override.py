# Beacon Contact Temperature Override
# Allows temporarily changing contact_max_hotend_temperature at runtime
# for thermal expansion calibration
#
# This is SAFER than RatOS approach (permanent high limit)
# We keep 185°C default and only raise during calibration

class BeaconTempOverride:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        self.original_temp = None

        self.gcode.register_command(
            'SET_BEACON_CONTACT_MAX_TEMP',
            self.cmd_SET_BEACON_CONTACT_MAX_TEMP,
            desc="Temporarily set Beacon contact max hotend temperature"
        )

    def cmd_SET_BEACON_CONTACT_MAX_TEMP(self, gcmd):
        temp = gcmd.get_float('TEMP', None)
        reset = gcmd.get_int('RESET', 0)

        # Find beacon object
        try:
            beacon = self.printer.lookup_object('beacon')
        except:
            raise gcmd.error("Beacon not found")

        # Access the contact probe
        if not hasattr(beacon, 'mcu_contact_probe'):
            raise gcmd.error("Beacon contact probe not available")

        contact_probe = beacon.mcu_contact_probe

        if reset:
            # Restore original temperature
            if self.original_temp is not None:
                contact_probe.max_hotend_temp = self.original_temp
                gcmd.respond_info("Restored contact_max_hotend_temperature to %.1f" % self.original_temp)
                self.original_temp = None
            else:
                gcmd.respond_info("No original temperature saved")
            return

        if temp is None:
            # Just show current value
            gcmd.respond_info("Current contact_max_hotend_temperature: %.1f" % contact_probe.max_hotend_temp)
            return

        # Save original if not already saved
        if self.original_temp is None:
            self.original_temp = contact_probe.max_hotend_temp

        # Set new temperature
        contact_probe.max_hotend_temp = temp
        gcmd.respond_info("Set contact_max_hotend_temperature to %.1f (was %.1f)" % (temp, self.original_temp))

def load_config(config):
    return BeaconTempOverride(config)
