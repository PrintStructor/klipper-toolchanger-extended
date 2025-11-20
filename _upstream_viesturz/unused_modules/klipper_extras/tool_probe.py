# Per-tool Z-Probe support
#
# Copyright (C) 2023
# Viesturs Zarins <viesturz@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.

import logging
from . import probe


class ToolProbe:
    """
    Represents a Z-probe attached to a specific toolhead in a multi-tool setup.
    Each tool can have its own dedicated probe pin and offset.
    """

    def __init__(self, config):
        self.tool = config.getint('tool')
        self.printer = config.get_printer()
        self.name = config.get_name()
        self.mcu_probe = probe.ProbeEndstopWrapper(config)
        self.probe_offsets = probe.ProbeOffsetsHelper(config)
        self.probe_session = ProbeSessionHelper(config, self.mcu_probe)

        # Crash detection configuration
        pin = config.get('pin')
        buttons = self.printer.load_object(config, 'buttons')
        ppins = self.printer.lookup_object('pins')
        ppins.allow_multi_use_pin(pin.replace('^', '').replace('!', ''))
        buttons.register_buttons([pin], self._button_handler)

        # Register this probe with the global [tool_probe_endstop] manager
        self.endstop = self.printer.load_object(config, "tool_probe_endstop")
        self.endstop.add_probe(config, self)

    def _button_handler(self, eventtime, is_triggered):
        """Event handler triggered when the probe pin changes state."""
        self.endstop.note_probe_triggered(self, eventtime, is_triggered)

    def get_probe_params(self, gcmd=None):
        """Return the current probe parameters (speed, samples, etc.)."""
        return self.probe_session.get_probe_params(gcmd)

    def get_offsets(self):
        """Return the probe offset for this tool."""
        return self.probe_offsets.get_offsets()

    def start_probe_session(self, gcmd):
        """Begin a new probe session for this tool."""
        return self.probe_session.start_probe_session(gcmd)


# --------------------------------------------------------------------------- #
# Helper class to track multiple probe attempts within a single G-code command
# --------------------------------------------------------------------------- #
class ProbeSessionHelper:
    """
    Manages the state of a multi-sample probe operation, including retries,
    tolerances, lift distances, and cleanup on error.
    """

    def __init__(self, config, mcu_probe):
        self.printer = config.get_printer()
        self.mcu_probe = mcu_probe
        gcode = self.printer.lookup_object('gcode')
        self.dummy_gcode_cmd = gcode.create_gcode_command("", "", {})

        # Determine Z target position for probing moves
        if config.has_section('stepper_z'):
            zconfig = config.getsection('stepper_z')
            self.z_position = zconfig.getfloat('position_min', 0., note_valid=False)
        else:
            pconfig = config.getsection('printer')
            self.z_position = pconfig.getfloat('minimum_z_position', 0., note_valid=False)

        # Configurable probing speeds
        self.speed = config.getfloat('speed', 5.0, above=0.)
        self.lift_speed = config.getfloat('lift_speed', self.speed, above=0.)

        # Multi-sampling support (for improved accuracy)
        self.sample_count = config.getint('samples', 1, minval=1)
        self.sample_retract_dist = config.getfloat('sample_retract_dist', 2., above=0.)
        atypes = {'median': 'median', 'average': 'average'}
        self.samples_result = config.getchoice('samples_result', atypes, 'average')
        self.samples_tolerance = config.getfloat('samples_tolerance', 0.100, minval=0.)
        self.samples_retries = config.getint('samples_tolerance_retries', 0, minval=0)

        # Runtime session state
        self.multi_probe_pending = False
        self.results = []

        # Register event handlers for cleanup
        self.printer.register_event_handler("gcode:command_error", self._handle_command_error)

    def _handle_command_error(self):
        """Ensure probe sessions are closed properly after an error."""
        if self.multi_probe_pending:
            try:
                self.end_probe_session()
            except Exception:
                logging.exception("Error while ending multi-probe session after command failure")

    def _probe_state_error(self):
        """Raise an error when probe session start/end calls are mismatched."""
        raise self.printer.command_error(
            "Internal probe state error — start/end probe session mismatch"
        )

    def start_probe_session(self, gcmd):
        """Start a new multi-probe session."""
        if self.multi_probe_pending:
            self._probe_state_error()
        self.mcu_probe.multi_probe_begin()
        self.multi_probe_pending = True
        self.results = []
        return self

    def end_probe_session(self):
        """End an ongoing multi-probe session and clear any temporary state."""
        if not self.multi_probe_pending:
            self._probe_state_error()
        self.results = []
        self.multi_probe_pending = False
        self.mcu_probe.multi_probe_end()

    def get_probe_params(self, gcmd=None):
        """Resolve probe parameters from G-code or defaults."""
        if gcmd is None:
            gcmd = self.dummy_gcode_cmd
        probe_speed = gcmd.get_float("PROBE_SPEED", self.speed, above=0.)
        lift_speed = gcmd.get_float("LIFT_SPEED", self.lift_speed, above=0.)
        samples = gcmd.get_int("SAMPLES", self.sample_count, minval=1)
        sample_retract_dist = gcmd.get_float(
            "SAMPLE_RETRACT_DIST", self.sample_retract_dist, above=0.
        )
        samples_tolerance = gcmd.get_float(
            "SAMPLES_TOLERANCE", self.samples_tolerance, minval=0.
        )
        samples_retries = gcmd.get_int(
            "SAMPLES_TOLERANCE_RETRIES", self.samples_retries, minval=0
        )
        samples_result = gcmd.get("SAMPLES_RESULT", self.samples_result)
        return {
            'probe_speed': probe_speed,
            'lift_speed': lift_speed,
            'samples': samples,
            'sample_retract_dist': sample_retract_dist,
            'samples_tolerance': samples_tolerance,
            'samples_tolerance_retries': samples_retries,
            'samples_result': samples_result,
        }

    def _probe(self, speed):
        """Perform a single probing move and return the result position."""
        toolhead = self.printer.lookup_object('toolhead')
        curtime = self.printer.get_reactor().monotonic()
        if 'z' not in toolhead.get_status(curtime)['homed_axes']:
            raise self.printer.command_error("Must home before probing")

        pos = toolhead.get_position()
        pos[2] = self.z_position

        try:
            phoming = self.printer.lookup_object('homing')
            epos = phoming.probing_move(self.mcu_probe, pos, speed)
        except self.printer.command_error as e:
            reason = str(e)
            if "Timeout during endstop homing" in reason:
                reason += probe.HINT_TIMEOUT
            raise self.printer.command_error(reason)

        # Allow axis_twist_compensation and similar modules to consume probe data
        self.printer.send_event("probe:update_results", epos)

        # Report to terminal
        gcode = self.printer.lookup_object('gcode')
        gcode.respond_info("Probe contact at X=%.3f Y=%.3f Z=%.6f"
                           % (epos[0], epos[1], epos[2]))
        return epos[:3]

    def run_probe(self, gcmd):
        """Perform the actual probing process with sampling and retries."""
        if not self.multi_probe_pending:
            self._probe_state_error()

        params = self.get_probe_params(gcmd)
        toolhead = self.printer.lookup_object('toolhead')
        probexy = toolhead.get_position()[:2]
        retries = 0
        positions = []
        sample_count = params['samples']

        while len(positions) < sample_count:
            # Perform probe move
            pos = self._probe(params['probe_speed'])
            positions.append(pos)

            # Check sample tolerance
            z_positions = [p[2] for p in positions]
            if max(z_positions) - min(z_positions) > params['samples_tolerance']:
                if retries >= params['samples_tolerance_retries']:
                    raise gcmd.error("Probe samples exceed samples_tolerance")
                gcmd.respond_info("Probe samples exceeded tolerance — retrying...")
                retries += 1
                positions = []
            # Retract if more samples needed
            if len(positions) < sample_count:
                toolhead.manual_move(
                    probexy + [pos[2] + params['sample_retract_dist']],
                    params['lift_speed']
                )

        # Compute final averaged/median result
        epos = probe.calc_probe_z_average(positions, params['samples_result'])
        self.results.append(epos)

    def pull_probed_results(self):
        """Return and clear all accumulated probe results."""
        res = self.results
        self.results = []
        return res


def load_config_prefix(config):
    """Entry point for Klipper module loader."""
    return ToolProbe(config)