# Nozzle alignment module for 3d kinematic probes.
#
# Copyright (C) Kevin O'Connor <kevin@koconnor.net>
# Copyright (C) Martin Hierholzer <martin@hierholzer.info>
# Original work Copyright (C) 2023 Viesturs Zarins <viesturz@gmail.com>
# Modified work Copyright (C) 2025 PrintStructor
#
# This is an enhanced fork based on Viesturz's klipper-toolchanger project
# Original: https://github.com/viesturz/klipper-toolchanger
# Enhanced Fork: https://github.com/PrintStructor/klipper-toolchanger
#
# Major enhancements in this fork:
# - Initial tool tracking for relative offset calibration
# - XY-offset matrix support and auto-save to config
# - Separation of XY calibration from Z (Beacon-based)
# - Improved sensor location workflow
#
# Adapted from: https://github.com/ben5459/Klipper_ToolChanger/blob/master/probe_multi_axis.py
#
# This file may be distributed under the terms of the GNU GPLv3 license.

import logging

direction_types = {'x+': [0, +1], 'x-': [0, -1], 'y+': [1, +1], 'y-': [1, -1],
                   'z+': [2, +1], 'z-': [2, -1]}

HINT_TIMEOUT = """
If the probe did not move far enough to trigger, then
consider reducing/increasing the axis minimum/maximum
position so the probe can travel further (the minimum
position can be negative).
"""


class ToolsCalibrate:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name()
        self.gcode_move = self.printer.load_object(config, "gcode_move")
        self.probe_multi_axis = PrinterProbeMultiAxis(config,
                                                      ProbeEndstopWrapper(
                                                          config, 'x'),
                                                      ProbeEndstopWrapper(
                                                          config, 'y'),
                                                      ProbeEndstopWrapper(
                                                          config, 'z'))
        self.probe_name = config.get('probe', 'probe')
        self.travel_speed = config.getfloat('travel_speed', 10.0, above=0.)
        self.spread = config.getfloat('spread', 5.0)
        self.lower_z = config.getfloat('lower_z', 0.5)
        self.lift_z = config.getfloat('lift_z', 1.0)
        self.trigger_to_bottom_z = config.getfloat('trigger_to_bottom_z',
                                                   default=0.0)
        self.lift_speed = config.getfloat('lift_speed',
                                          self.probe_multi_axis.lift_speed)
        self.final_lift_z = config.getfloat('final_lift_z', 4.0)
        self.sensor_location = None
        self.last_result = [0., 0., 0.]
        self.last_probe_offset = 0.
        self.calibration_probe_inactive = True
        self.initial_tool = None  # Store the initial tool
        self.initial_location = None  # Store the initial tool position
        
        # Register commands
        self.gcode = self.printer.lookup_object('gcode')
        self.gcode.register_command('TOOL_LOCATE_SENSOR',
                                    self.cmd_TOOL_LOCATE_SENSOR,
                                    desc=self.cmd_TOOL_LOCATE_SENSOR_help)
        self.gcode.register_command('TOOL_CALIBRATE_TOOL_OFFSET',
                                    self.cmd_TOOL_CALIBRATE_TOOL_OFFSET,
                                    desc=self.cmd_TOOL_CALIBRATE_TOOL_OFFSET_help)
        self.gcode.register_command('TOOL_CALIBRATE_SAVE_TOOL_OFFSET',
                                    self.cmd_TOOL_CALIBRATE_SAVE_TOOL_OFFSET,
                                    desc=self.cmd_TOOL_CALIBRATE_SAVE_TOOL_OFFSET_help)
        self.gcode.register_command('TOOL_CALIBRATE_PROBE_OFFSET',
                                    self.cmd_TOOL_CALIBRATE_PROBE_OFFSET,
                                    desc=self.cmd_TOOL_CALIBRATE_PROBE_OFFSET_help)
        self.gcode.register_command('TOOL_CALIBRATE_QUERY_PROBE',
                                    self.cmd_TOOL_CALIBRATE_QUERY_PROBE,
                                    desc=self.cmd_TOOL_CALIBRATE_QUERY_PROBE_help)
        self.gcode.register_command('TOOL_SAVE_Z_OFFSET',
                                    self.cmd_TOOL_SAVE_Z_OFFSET,
                                    desc=self.cmd_TOOL_SAVE_Z_OFFSET_help)
 
    def probe_xy(self, toolhead, top_pos, direction, gcmd, samples=None):
        offset = direction_types[direction]
        start_pos = list(top_pos)
        start_pos[offset[0]] -= offset[1] * self.spread
        toolhead.manual_move([None, None, top_pos[2] + self.lift_z],
                             self.lift_speed)
        toolhead.manual_move([start_pos[0], start_pos[1], None],
                             self.travel_speed)
        toolhead.manual_move([None, None, top_pos[2] - self.lower_z],
                             self.lift_speed)
        return self.probe_multi_axis.run_probe(direction, gcmd, samples=samples,
                                               max_distance=self.spread * 1.8)[
            offset[0]]

    def calibrate_xy(self, toolhead, top_pos, gcmd, samples=None):
        left_x = self.probe_xy(toolhead, top_pos, 'x+', gcmd, samples=samples)
        right_x = self.probe_xy(toolhead, top_pos, 'x-', gcmd, samples=samples)
        near_y = self.probe_xy(toolhead, top_pos, 'y+', gcmd, samples=samples)
        far_y = self.probe_xy(toolhead, top_pos, 'y-', gcmd, samples=samples)
        return [(left_x + right_x) / 2., (near_y + far_y) / 2.]

    def locate_sensor(self, gcmd):
        toolhead = self.printer.lookup_object('toolhead')
        position = toolhead.get_position()
        downPos = self.probe_multi_axis.run_probe("z-", gcmd, samples=1)
        center_x, center_y = self.calibrate_xy(toolhead, downPos, gcmd,
                                               samples=1)

        toolhead.manual_move([None, None, downPos[2] + self.lift_z],
                             self.lift_speed)
        toolhead.manual_move([center_x, center_y, None], self.travel_speed)
        center_z = self.probe_multi_axis.run_probe("z-", gcmd, speed_ratio=0.5)[
            2]
        # Now redo X and Y, since we have a more accurate center.
        center_x, center_y = self.calibrate_xy(toolhead,
                                               [center_x, center_y, center_z],
                                               gcmd)

        # rest above center
        position[0] = center_x
        position[1] = center_y
        position[2] = center_z + self.final_lift_z
        toolhead.manual_move([None, None, position[2]], self.lift_speed)
        toolhead.manual_move([position[0], position[1], None],
                             self.travel_speed)
        toolhead.set_position(position)
        return [center_x, center_y, center_z]

    cmd_TOOL_LOCATE_SENSOR_help = ("Locate the tool calibration sensor, "
                                   "use with tool 0.")

    def cmd_TOOL_LOCATE_SENSOR(self, gcmd):
        """Modified version that stores the current tool as the initial tool"""
        toolhead = self.printer.lookup_object('toolhead')
        self.initial_tool = self.printer.lookup_object('toolchanger').get_selected_tool()
        if not self.initial_tool:
            raise gcmd.error("No tool selected for TOOL_LOCATE_SENSOR")
            
        self.last_result = self.locate_sensor(gcmd)
        self.sensor_location = self.last_result
        self.initial_location = self.last_result  # Store the initial tool position
        
        # Set the initial tool's X-Y offsets to 0
        self.gcode.run_script_from_command("SET_GCODE_OFFSET X=0 Y=0")
        
        # Clear ALL offset dictionaries in the tool object itself (for runtime)
        # This ensures that during calibration, all toolchanges use 0 offsets
        max_tool_count = self.printer.lookup_object('toolchanger').params.get('max_tool_count', 6)
        for i in range(max_tool_count):
            if i != self.initial_tool.tool_number:
                self.initial_tool.xy_offsets[i] = [0.0, 0.0]
                self.initial_tool.z_offsets[i] = 0.0
        
        # Save ONLY XY offsets to config (Z-offsets will be written by Beacon calibration)
        configfile = self.printer.lookup_object('configfile')
        for i in range(max_tool_count):
            if i != self.initial_tool.tool_number:
                configfile.set(self.initial_tool.name, f't{i}_xy_offset', "0.000000, 0.000000")
        
        self.gcode.respond_info("Initial tool %s sensor location at X=%.6f, Y=%.6f, Z=%.6f"
                            % (self.initial_tool.name, self.last_result[0], 
                               self.last_result[1], self.last_result[2]))
        self.gcode.respond_info("XY offsets cleared in config, Z offsets cleared in memory only (will be set by Beacon)")

    cmd_TOOL_CALIBRATE_TOOL_OFFSET_help = "Calibrate current tool offset relative to tool 0"

    def cmd_TOOL_CALIBRATE_TOOL_OFFSET(self, gcmd):
        """Calibrates XY offsets relative to the initial tool and displays Z for reference"""
        if not self.initial_location:
            raise gcmd.error(
                "No recorded initial tool location, please run TOOL_LOCATE_SENSOR first")
        
        # Get current tool
        current_tool = self.printer.lookup_object('toolchanger').get_selected_tool()
        if not current_tool:
            raise gcmd.error("No tool selected for calibration")
            
        # If it is the initial tool, set XY offsets to 0 (preserve Z-offsets in config but clear runtime offset)
        if current_tool == self.initial_tool:
            self.gcode.run_script_from_command("SET_GCODE_OFFSET X=0 Y=0 Z=0")
            # Save only XY offsets to 0.00 for initial tool (Z-offsets are preserved)
            max_tool_count = self.printer.lookup_object('toolchanger').params.get('max_tool_count', 6)
            configfile = self.printer.lookup_object('configfile')
            for i in range(max_tool_count):
                if i != self.initial_tool.tool_number:
                    configfile.set(self.initial_tool.name, f't{i}_xy_offset', "0.000000, 0.000000")
            self.gcode.respond_info(f"Initial tool {self.initial_tool.name}: XY offsets set to 0.00, Z runtime offset cleared (Z-offsets in config preserved)")
            return
            
        # Measure the current tool's position
        location = self.locate_sensor(gcmd)
        
        # Compute ALL offsets relative to the initial tool (including Z for display)
        x_offset = location[0] - self.initial_location[0]
        y_offset = location[1] - self.initial_location[1]
        z_offset = location[2] - self.initial_location[2]
        
        # Save ONLY XY-offsets to config (Z is for reference only)
        # Store in initial tool's section for consistency with Z-offsets
        configfile = self.printer.lookup_object('configfile')
        configfile.set(self.initial_tool.name, f't{current_tool.tool_number}_xy_offset',
                      f"{x_offset:.6f}, {y_offset:.6f}")
        
        # Apply ONLY XY-offsets, clear Z runtime offset (Z-offsets in config are preserved)
        self.gcode.run_script_from_command(
            f"SET_GCODE_OFFSET X={x_offset:.6f} Y={y_offset:.6f} Z=0")
        
        # Store all three for reference (Z is display-only)
        self.last_result = [x_offset, y_offset, z_offset]
        
        # Enhanced output with Z for comparison
        self.gcode.respond_info(
            f"Tool {current_tool.name} offsets relative to {self.initial_tool.name}:\n"
            f"  XY (saved):      X={x_offset:.6f}, Y={y_offset:.6f}\n"
            f"  Z (reference):   {z_offset:.6f} (use BEACON for actual Z-offset)")

    cmd_TOOL_CALIBRATE_SAVE_TOOL_OFFSET_help = "Save tool offset calibration to config"

    def cmd_TOOL_CALIBRATE_SAVE_TOOL_OFFSET(self, gcmd):
        if not self.last_result:
            gcmd.error(
                "No offset result, please run TOOL_CALIBRATE_TOOL_OFFSET first")
            return
        section_name = gcmd.get("SECTION")
        param_name = gcmd.get("ATTRIBUTE")
        template = gcmd.get("VALUE", "{x:0.6f}, {y:0.6f}, {z:0.6f}")
        value = template.format(x=self.last_result[0], y=self.last_result[1],
                                z=self.last_result[2])
        configfile = self.printer.lookup_object('configfile')
        configfile.set(section_name, param_name, value)

    cmd_TOOL_CALIBRATE_PROBE_OFFSET_help = "Calibrate the tool probe offset to nozzle tip"

    def cmd_TOOL_CALIBRATE_PROBE_OFFSET(self, gcmd):
        toolhead = self.printer.lookup_object('toolhead')
        probe = self.printer.lookup_object(self.probe_name)
        start_pos = toolhead.get_position()
        nozzle_z = self.probe_multi_axis.run_probe("z-", gcmd, speed_ratio=0.5)[
            2]
        # now move down with the tool probe
        probe_session = probe.start_probe_session(gcmd)
        probe_session.run_probe(gcmd)
        probe_z = probe_session.pull_probed_results()[0][2]
        probe_session.end_probe_session()

        z_offset = probe_z - nozzle_z + self.trigger_to_bottom_z
        self.last_probe_offset = z_offset
        self.gcode.respond_info(
            "%s: z_offset: %.3f\n"
            "The SAVE_CONFIG command will update the printer config file\n"
            "with the above and restart the printer." % (
            self.probe_name, z_offset))
        config_name = gcmd.get("PROBE", default=self.probe_name)
        if config_name:
            configfile = self.printer.lookup_object('configfile')
            configfile.set(config_name, 'z_offset', "%.6f" % (z_offset,))
        # back to start pos
        toolhead.move(start_pos, self.travel_speed)
        toolhead.set_position(start_pos)

    def get_status(self, eventtime):
        return {'last_result': self.last_result,
                'last_probe_offset': self.last_probe_offset,
                'calibration_probe_inactive': self.calibration_probe_inactive,
                'last_x_result': self.last_result[0],
                'last_y_result': self.last_result[1],
                'last_z_result': self.last_result[2]}

    cmd_TOOL_CALIBRATE_QUERY_PROBE_help = "Return the state of calibration probe"
    def cmd_TOOL_CALIBRATE_QUERY_PROBE(self, gcmd):
        toolhead = self.printer.lookup_object('toolhead')
        print_time = toolhead.get_last_move_time()
        endstop_states = [probe.query_endstop(print_time) for probe in self.probe_multi_axis.mcu_probe]  # Check the state of each axis probe (x, y, z)
        self.calibration_probe_inactive = any(endstop_states)
        gcmd.respond_info("Calibration Probe: %s" % (["open", "TRIGGERED"][any(endstop_states)]))

    cmd_TOOL_SAVE_Z_OFFSET_help = "Save Z-offset for a tool relative to initial tool"
    def cmd_TOOL_SAVE_Z_OFFSET(self, gcmd):
        """Save Z-offset for a tool relative to initial tool (used by Beacon calibration)"""
        tool_number = gcmd.get_int('TOOL')
        z_offset = gcmd.get_float('OFFSET')
        
        if not self.initial_tool:
            raise gcmd.error("No initial tool set. Run TOOL_LOCATE_SENSOR first")
        
        # Get the tool object
        tool = self.printer.lookup_object('toolchanger').lookup_tool(tool_number)
        if not tool:
            raise gcmd.error(f"Tool T{tool_number} not found")
        
        # Save to config
        configfile = self.printer.lookup_object('configfile')
        configfile.set(tool.name, f't{self.initial_tool.tool_number}_z_offset',
                      f"{z_offset:.6f}")
        
        gcmd.respond_info(f"Saved T{tool_number} Z-offset relative to T{self.initial_tool.tool_number}: {z_offset:.6f}")

class PrinterProbeMultiAxis:
    def __init__(self, config, mcu_probe_x, mcu_probe_y, mcu_probe_z):
        self.printer = config.get_printer()
        self.name = config.get_name()
        self.mcu_probe = [mcu_probe_x, mcu_probe_y, mcu_probe_z]
        self.speed = config.getfloat('speed', 5.0, above=0.)
        self.lift_speed = config.getfloat('lift_speed', self.speed, above=0.)
        self.max_travel = config.getfloat("max_travel", 4, above=0)
        self.last_state = False
        self.last_result = [0., 0., 0.]
        self.last_x_result = 0.
        self.last_y_result = 0.
        self.last_z_result = 0.
        self.gcode = self.printer.lookup_object('gcode')
        self.gcode_move = self.printer.load_object(config, "gcode_move")

        # Multi-sample support (for improved accuracy)
        self.sample_count = config.getint('samples', 1, minval=1)
        self.sample_retract_dist = config.getfloat('sample_retract_dist', 2.,
                                                   above=0.)
        atypes = {'median': 'median', 'average': 'average'}
        self.samples_result = config.getchoice('samples_result', atypes,
                                               'average')
        self.samples_tolerance = config.getfloat('samples_tolerance', 0.100,
                                                 minval=0.)
        self.samples_retries = config.getint('samples_tolerance_retries', 0,
                                             minval=0)
        # Register xyz_virtual_endstop pin
        self.printer.lookup_object('pins').register_chip('probe_multi_axis',
                                                         self)

    def setup_pin(self, pin_type, pin_params):
        if pin_type != 'endstop' or pin_params['pin'] != 'xy_virtual_endstop':
            raise pins.error("Probe virtual endstop only useful as endstop pin")
        if pin_params['invert'] or pin_params['pullup']:
            raise pins.error("Can not pullup/invert probe virtual endstop")
        return self.mcu_probe

    def get_lift_speed(self, gcmd=None):
        if gcmd is not None:
            return gcmd.get_float("LIFT_SPEED", self.lift_speed, above=0.)
        return self.lift_speed

    def _probe(self, speed, axis, sense, max_distance):
        phoming = self.printer.lookup_object('homing')
        pos = self._get_target_position(axis, sense, max_distance)
        try:
            epos = phoming.probing_move(self.mcu_probe[axis], pos, speed)
        except self.printer.command_error as e:
            reason = str(e)
            if "Timeout during endstop homing" in reason:
                reason += HINT_TIMEOUT
            raise self.printer.command_error(reason)
        # self.gcode.respond_info("probe at %.3f,%.3f is z=%.6f"
        self.gcode.respond_info("Probe made contact at %.6f,%.6f,%.6f"
                                % (epos[0], epos[1], epos[2]))
        return epos[:3]

    def _get_target_position(self, axis, sense, max_distance):
        toolhead = self.printer.lookup_object('toolhead')
        curtime = self.printer.get_reactor().monotonic()
        if 'x' not in toolhead.get_status(curtime)['homed_axes'] or \
                'y' not in toolhead.get_status(curtime)['homed_axes'] or \
                'z' not in toolhead.get_status(curtime)['homed_axes']:
            raise self.printer.command_error("Must home before probe")
        pos = toolhead.get_position()
        kin_status = toolhead.get_kinematics().get_status(curtime)
        if 'axis_minimum' not in kin_status or 'axis_minimum' not in kin_status:
            raise self.gcode.error(
                "Tools calibrate only works with cartesian kinematics")
        if sense > 0:
            pos[axis] = min(pos[axis] + max_distance,
                            kin_status['axis_maximum'][axis])
        else:
            pos[axis] = max(pos[axis] - max_distance,
                            kin_status['axis_minimum'][axis])
        return pos

    def _move(self, coord, speed):
        self.printer.lookup_object('toolhead').manual_move(coord, speed)

    def _calc_mean(self, positions):
        count = float(len(positions))
        return [sum([pos[i] for pos in positions]) / count
                for i in range(3)]

    def _calc_median(self, positions, axis):
        axis_sorted = sorted(positions, key=(lambda p: p[axis]))
        middle = len(positions) // 2
        if (len(positions) & 1) == 1:
            # odd number of samples
            return axis_sorted[middle]
        # even number of samples
        return self._calc_mean(axis_sorted[middle - 1:middle + 1])

    def run_probe(self, direction, gcmd, speed_ratio=1.0, samples=None,
                  max_distance=100.0):
        speed = gcmd.get_float("PROBE_SPEED", self.speed,
                               above=0.) * speed_ratio
        if direction not in direction_types:
            raise self.printer.command_error("Wrong value for DIRECTION.")

        logging.info("run_probe direction = %s" % (direction,))

        (axis, sense) = direction_types[direction]

        logging.info("run_probe axis = %d, sense = %d" % (axis, sense))

        lift_speed = self.get_lift_speed(gcmd)
        sample_count = gcmd.get_int("SAMPLES",
                                    samples if samples else self.sample_count,
                                    minval=1)
        sample_retract_dist = gcmd.get_float("SAMPLE_RETRACT_DIST",
                                             self.sample_retract_dist, above=0.)
        samples_tolerance = gcmd.get_float("SAMPLES_TOLERANCE",
                                           self.samples_tolerance, minval=0.)
        samples_retries = gcmd.get_int("SAMPLES_TOLERANCE_RETRIES",
                                       self.samples_retries, minval=0)
        samples_result = gcmd.get("SAMPLES_RESULT", self.samples_result)

        probe_start = self.printer.lookup_object('toolhead').get_position()
        retries = 0
        positions = []
        while len(positions) < sample_count:
            # Probe position
            pos = self._probe(speed, axis, sense, max_distance)
            positions.append(pos)
            # Check samples tolerance
            axis_positions = [p[axis] for p in positions]
            if max(axis_positions) - min(axis_positions) > samples_tolerance:
                if retries >= samples_retries:
                    raise gcmd.error("Probe samples exceed samples_tolerance")
                gcmd.respond_info("Probe samples exceed tolerance. Retrying...")
                retries += 1
                positions = []
            # Retract
            if len(positions) < sample_count:
                liftpos = probe_start
                liftpos[axis] = pos[axis] - sense * sample_retract_dist
                self._move(liftpos, lift_speed)
        # Calculate and return result
        if samples_result == 'median':
            return self._calc_median(positions, axis)
        return self._calc_mean(positions)


# Endstop wrapper that enables probe specific features
class ProbeEndstopWrapper:
    def __init__(self, config, axis):
        self.printer = config.get_printer()
        self.axis = axis
        self.idex = config.has_section('dual_carriage') or config.has_section('dual_carriage u')
        # Create an "endstop" object to handle the probe pin
        ppins = self.printer.lookup_object('pins')
        pin = config.get('pin')
        ppins.allow_multi_use_pin(pin.replace('^', '').replace('!', ''))
        pin_params = ppins.lookup_pin(pin, can_invert=True, can_pullup=True)
        mcu = pin_params['chip']
        self.mcu_endstop = mcu.setup_pin('endstop', pin_params)
        self.printer.register_event_handler('klippy:mcu_identify',
                                            self._handle_mcu_identify)
        # Wrappers
        self.get_mcu = self.mcu_endstop.get_mcu
        self.add_stepper = self.mcu_endstop.add_stepper
        self.get_steppers = self._get_steppers
        self.home_start = self.mcu_endstop.home_start
        self.home_wait = self.mcu_endstop.home_wait
        self.query_endstop = self.mcu_endstop.query_endstop

    def _get_steppers(self):
        if self.idex and self.axis == 'x':
            dual_carriage = self.printer.lookup_object('dual_carriage')
            axis = "xyz".index(self.axis)
            prime_rail = dual_carriage.get_primary_rail(axis)
            return prime_rail.get_steppers()
        else:
            return self.mcu_endstop.get_steppers()

    def _handle_mcu_identify(self):
        kin = self.printer.lookup_object('toolhead').get_kinematics()
        for stepper in kin.get_steppers():
            if stepper.is_active_axis(self.axis):
                self.add_stepper(stepper)

    def get_position_endstop(self):
        return 0.


def load_config(config):
    return ToolsCalibrate(config)
