# Support for toolchangers
#
# Original work Copyright (C) 2023 Viesturs Zarins <viesturz@gmail.com>
# Modified work Copyright (C) 2025 PrintStructor
#
# This is an enhanced fork based on Viesturz's klipper-toolchanger project
# Original: https://github.com/viesturz/klipper-toolchanger
# Enhanced Fork: https://github.com/PrintStructor/klipper-toolchanger
#
# Major enhancements in this fork:
# - Stage-based tool pickup/dropoff (stage1 + stage2)
# - Non-fatal error handling (pause instead of shutdown)
# - Tool detection polling and verification
# - Motion flush & position freeze on errors
# - Baby-stepping with global Z-offset management
# - Initial tool tracking for relative offsets
# - Extended commands (RESET_INITIAL_TOOL, RESET_TOOLCHANGER_STATUS)
# - Graceful error recovery system
#
# This file may be distributed under the terms of the GNU GPLv3 license.

import ast, bisect
from unittest.mock import sentinel

# ==============================================================================
#                              Constants
# ==============================================================================

STATUS_UNINITALIZED = 'uninitialized'
STATUS_INITIALIZING = 'initializing'
STATUS_READY = 'ready'
STATUS_CHANGING = 'changing'
STATUS_ERROR = 'error'
INIT_ON_HOME = 0
INIT_MANUAL = 1
INIT_FIRST_USE = 2
ON_AXIS_NOT_HOMED_ABORT = 0
ON_AXIS_NOT_HOMED_HOME = 1
XYZ_TO_INDEX = {'x': 0, 'X': 0, 'y': 1, 'Y': 1, 'z': 2, 'Z': 2}
INDEX_TO_XYZ = 'XYZ'
DETECT_UNAVAILABLE = -1
DETECT_ABSENT = 0
DETECT_PRESENT = 1


class Toolchanger:
    def __init__(self, config):
        # ==============================================================================
        #                          Initialization
        # ==============================================================================
        self.printer = config.get_printer()
        self.config = config
        self.gcode_macro = self.printer.load_object(config, 'gcode_macro')
        self.gcode = self.printer.lookup_object('gcode')
        self.gcode_move = self.printer.load_object(config, 'gcode_move')

        self.name = config.get_name()
        self.params = get_params_dict(config)
        init_options = {'home': INIT_ON_HOME,
                        'manual': INIT_MANUAL, 'first-use': INIT_FIRST_USE}
        self.initialize_on = config.getchoice(
            'initialize_on', init_options, 'first-use')
        self.verify_tool_pickup = config.getboolean('verify_tool_pickup', True)
<<<<<<< HEAD
        self.verify_tool_dropoff = config.getboolean('verify_tool_dropoff', False)
=======
        self.require_tool_present = config.getboolean('require_tool_present', False)
        self.transfer_fan_speed = config.getboolean('transfer_fan_speed', True)
>>>>>>> a85befe6eab3ab4da6a1de283d80b69f64b8dee7
        self.uses_axis = config.get('uses_axis', 'xyz').lower()
        home_options = {'abort': ON_AXIS_NOT_HOMED_ABORT,
                        'home': ON_AXIS_NOT_HOMED_HOME}
        self.on_axis_not_homed = config.getchoice('on_axis_not_homed',
                                                  home_options, 'abort')
        self.initialize_gcode = self.gcode_macro.load_template(
            config, 'initialize_gcode', '')
        self.error_gcode = self.gcode_macro.load_template(config, 'error_gcode') if config.get('error_gcode', None) else None
        self.default_before_change_gcode = self.gcode_macro.load_template(
            config, 'before_change_gcode', '')
        self.default_after_change_gcode = self.gcode_macro.load_template(
            config, 'after_change_gcode', '')
        # Error-handling template
        self.error_gcode = self.gcode_macro.load_template(
            config, 'error_gcode', '')

        # Read all the fields that might be defined on toolchanger.
        # To avoid throwing config error when no tools configured.
        config.get('pickup_gcode', None)
        config.get('dropoff_gcode', None)
        config.get('recover_gcode', None)
        config.getfloat('gcode_x_offset', None)
        config.getfloat('gcode_y_offset', None)
        config.getfloat('gcode_z_offset', None)
        config.get('t_command_restore_axis', None)
        config.get('extruder', None)
        config.get('fan', None)
        config.get_prefix_options('params_')

        self.status = STATUS_UNINITALIZED
        self.active_tool = None
        self.initial_tool = None
        self.detected_tool = None
        self.has_detection = False
        self.tools = {}
        self.tool_numbers = []  # Ordered list of registered tool numbers.
        self.tool_names = []    # Tool names, in the same order as numbers.
        self.error_message = ''
<<<<<<< HEAD
        
        # Calibration mode flag - disables Z-offset application during measurements
        self.calibration_mode = False
=======
        self.next_change_id = 1
        self.current_change_id = -1
>>>>>>> a85befe6eab3ab4da6a1de283d80b69f64b8dee7

        self.printer.register_event_handler("homing:home_rails_begin",
                                            self._handle_home_rails_begin)
        self.printer.register_event_handler('klippy:connect',
                                            self._handle_connect)
        self.printer.register_event_handler("klippy:shutdown",
                                            self._handle_shutdown)
        self.gcode.register_command("INITIALIZE_TOOLCHANGER",
                                    self.cmd_INITIALIZE_TOOLCHANGER,
                                    desc=self.cmd_INITIALIZE_TOOLCHANGER_help)
        self.gcode.register_command("SET_TOOL_TEMPERATURE",
                                    self.cmd_SET_TOOL_TEMPERATURE,
                                    desc=self.cmd_SET_TOOL_TEMPERATURE_help)
        self.gcode.register_command("SELECT_TOOL",
                                    self.cmd_SELECT_TOOL,
                                    desc=self.cmd_SELECT_TOOL_help)
        self.gcode.register_command("SELECT_TOOL_ERROR",
                                    self.cmd_SELECT_TOOL_ERROR,
                                    desc=self.cmd_SELECT_TOOL_ERROR_help)
        if not self.require_tool_present:
            self.gcode.register_command("UNSELECT_TOOL",
                                        self.cmd_UNSELECT_TOOL,
                                        desc=self.cmd_UNSELECT_TOOL_help)
        self.gcode.register_command("TEST_TOOL_DOCKING",
                                    self.cmd_TEST_TOOL_DOCKING,
                                    desc=self.cmd_TEST_TOOL_DOCKING_help)
        self.gcode.register_command("SET_TOOL_PARAMETER",
                                    self.cmd_SET_TOOL_PARAMETER)
        self.gcode.register_command("RESET_TOOL_PARAMETER",
                                    self.cmd_RESET_TOOL_PARAMETER)
        self.gcode.register_command("SAVE_TOOL_PARAMETER",
                                    self.cmd_SAVE_TOOL_PARAMETER)
        self.gcode.register_command("VERIFY_TOOL_DETECTED",
                                    self.cmd_VERIFY_TOOL_DETECTED)
<<<<<<< HEAD
=======
        self.fan_switcher = None
        self.validate_tool_timer = None
>>>>>>> a85befe6eab3ab4da6a1de283d80b69f64b8dee7

        # Override SET_GCODE_OFFSET to hook baby-stepping
        gcode = self.printer.lookup_object('gcode')
        gcode.register_command('SET_GCODE_OFFSET', None)
        self.base_set_gcode_offset = self.gcode_move.cmd_SET_GCODE_OFFSET
        self.gcode.register_command("SET_GCODE_OFFSET",
                                    self.cmd_SET_GCODE_OFFSET,
                                    desc=self.cmd_SET_GCODE_OFFSET_help)
        self.gcode.register_command("RESET_INITIAL_TOOL",
                                    self.cmd_RESET_INITIAL_TOOL,
                                    desc="Reset the initial tool used as reference for tool offsets")
        self.gcode.register_command("RESET_TOOLCHANGER_STATUS",
                                    self.cmd_RESET_TOOLCHANGER_STATUS,
                                    desc=self.cmd_RESET_TOOLCHANGER_STATUS_help)
        self.gcode.register_command("RELOAD_TOOL_OFFSETS",
                                    self.cmd_RELOAD_TOOL_OFFSETS,
                                    desc=self.cmd_RELOAD_TOOL_OFFSETS_help)
        self.gcode.register_command("_SET_CALIBRATION_MODE",
                                    self.cmd_SET_CALIBRATION_MODE,
                                    desc="Internal: Enable/disable calibration mode")

    # ==============================================================================
    #                          Detection Helpers
    # ==============================================================================

    def _wait_for_detection_state(self, expected, expect_present, retries=10, delay=0.1):
        """Polls expected.detect_state; returns True if the desired state is reached."""
        toolhead = self.printer.lookup_object('toolhead')
        toolhead.wait_moves()
        reactor = self.printer.get_reactor()
        for i in range(retries):
            state = expected.detect_state
            if expect_present and state == DETECT_PRESENT:
                return True
            if not expect_present and state == DETECT_ABSENT:
                return True
            if i < retries - 1:
                reactor.pause(reactor.monotonic() + delay)
        # Timeout - don't log, will be handled by error_gcode
        return False

    def _flush_motion_and_freeze_position(self):
        """Stoppt geplante Moves und friert die aktuelle Position ein (kein Shutdown)."""
        try:
            self.gcode.run_script_from_command("M400")
            toolhead = self.printer.lookup_object('toolhead')
            self.gcode.run_script_from_command(
                "SET_KINEMATIC_POSITION X={x:.3f} Y={y:.3f} Z={z:.3f}".format(
                    x=toolhead.position[0], y=toolhead.position[1], z=toolhead.position[2]
                )
            )
            self.gcode.respond_info("⚠️ Planner flushed – queued moves canceled.")
        except Exception:
            pass

    # ==============================================================================
    #                          Graceful Error Handling
    # ==============================================================================

    def _pause_print(self):
        """Pause the print safely (no shutdown)."""
        try:
            self.printer.lookup_object('pause_resume').send_pause()
            self.gcode.respond_info("⏸️ Print paused due to toolchanger error")
        except Exception:
            try:
                self.gcode.run_script_from_command("PAUSE")
            except Exception:
                pass

    def _report_nonfatal(self, gcmd, message):
        """Report a non-fatal error without raising."""
        try:
            self.gcode.respond_info("!! Toolchanger Error: %s" % message)
            if gcmd is not None:
                gcmd.respond_info("!! Toolchanger Error: %s" % message)
        except Exception:
            pass
        return False

    # ==============================================================================
    #                                Lifecycle Hooks
    # ==============================================================================

    def _handle_babystep(self, z_adjust):
        """Handle baby-stepping adjustments for all tools."""
        try:
            globals_macro = self.printer.lookup_object('gcode_macro globals')
            current_offset = globals_macro.variables.get('global_z_offset', 0.06)
            new_offset = current_offset + z_adjust
            globals_macro.variables['global_z_offset'] = new_offset
            self.gcode.respond_info(
                "Updated global Z-offset to: %.3f (adjusted by %.3f)" %
                (new_offset, z_adjust))

            if self.initial_tool:
                for tool_num in self.tool_numbers:
                    if tool_num != self.initial_tool.tool_number:
                        tool = self.tools[tool_num]
                        if tool.tool_number in self.initial_tool.z_offsets:
                            tool_rel_offset = self.initial_tool.z_offsets[tool.tool_number]
                            new_total_offset = tool_rel_offset + new_offset
                            self.gcode.respond_info(
                                "Updated T%d offset to: %.3f" %
                                (tool_num, new_total_offset))
        except Exception as e:
            self.gcode.respond_info("Error updating global Z-offset: %s" % str(e))

    def _handle_home_rails_begin(self, homing_state, rails):
        if self.initialize_on == INIT_ON_HOME and self.status == STATUS_UNINITALIZED:
            self.initialize(self.detected_tool)

    def _handle_connect(self):
        self.status = STATUS_UNINITALIZED
        self.active_tool = None

    def _handle_shutdown(self):
        self.status = STATUS_UNINITALIZED
        self.active_tool = None

    def _process_error(self, message):
        """Centralized error handling for all toolchanger operations."""
        # prevent duplicate handling if already in error state    
        if self.status == STATUS_ERROR:
            # already handled; prevent duplicate pause/log flood
            return

        self.status = STATUS_ERROR
        self.error_message = message
        
        # only show minimal info (suppress repetitive debug spam)
        if not message.startswith("Script running error"):
            self.gcode.respond_info(f"⚠️ Toolchanger Error: {message}")
        
        if self.error_gcode:
            try:
                extra_context = {
                    'error_message': message,
                    'active_tool': self.active_tool.name if self.active_tool else "None",
                    'tool_number': self.active_tool.tool_number if self.active_tool else -1,
                }
                self.run_gcode('error_gcode', self.error_gcode, extra_context)
            except Exception as e:
                self.gcode.respond_info(f"Error executing error_gcode: {str(e)}")

    # ==============================================================================
    #                           UI & Status Helpers
    # ==============================================================================

    def get_status(self, eventtime):
        available_extruders = []
        for tool_num in self.tool_numbers:
            tool = self.tools[tool_num]
            if tool.extruder_name:
                available_extruders.append(tool.extruder_name)

        return {**self.params,
                'name': self.name,
                'status': self.status,
                'tool': self.active_tool.name if self.active_tool else None,
                'tool_number': self.active_tool.tool_number if self.active_tool else -1,
                'detected_tool': self.detected_tool.name if self.detected_tool else None,
                'detected_tool_number': self.detected_tool.tool_number if self.detected_tool else -1,
                'tool_numbers': self.tool_numbers,
                'tool_names': self.tool_names,
                'has_detection': self.has_detection,
                'available_extruders': available_extruders,
                }

    def _update_toolhead_extruders(self):
        """Update toolhead.available_extruders for UI highlighting."""
        try:
            toolhead = self.printer.lookup_object('toolhead')
            available_extruders = []
            for tool_num in self.tool_numbers:
                tool = self.tools[tool_num]
                if tool.extruder_name:
                    available_extruders.append(tool.extruder_name)
            if available_extruders:
                toolhead.all_extruders = available_extruders
                self.gcode.respond_info(
                    "UI: Updated toolhead.all_extruders with %d extruders" %
                    len(available_extruders))
        except Exception as e:
            self.gcode.respond_info("Warning: Could not update toolhead extruders: %s" % str(e))

    # ==============================================================================
    #                               Tool Registry
    # ==============================================================================

    def assign_tool(self, tool, number, prev_number, replace=False):
        if number in self.tools and not replace:
            # Config-time error (not a runtime command)
            raise Exception('Duplicate tools with number %s' % (number,))
        if prev_number in self.tools:
            del self.tools[prev_number]
            self.tool_numbers.remove(prev_number)
            self.tool_names.remove(tool.name)
        self.tools[number] = tool
        position = bisect.bisect_left(self.tool_numbers, number)
        self.tool_numbers.insert(position, number)
        self.tool_names.insert(position, tool.name)

        self.has_detection = any([t.detect_state != DETECT_UNAVAILABLE for t in self.tools.values()])
        all_detection = all([t.detect_state != DETECT_UNAVAILABLE for t in self.tools.values()])
        if self.has_detection and not all_detection:
            config = self.printer.lookup_object('configfile')
            # config error is fine (outside command path)
            raise config.error("Some tools missing detection pin")

        self._update_toolhead_extruders()

    # ==============================================================================
    #                              G-Code Commands
    # ==============================================================================

    cmd_INITIALIZE_TOOLCHANGER_help = "Initialize the toolchanger"
    def cmd_INITIALIZE_TOOLCHANGER(self, gcmd):
<<<<<<< HEAD
        tool = self._gcmd_tool(gcmd, None)
        if tool is None and self.has_detection:
            tool = self.require_detected_tool(gcmd)
            if tool is None:
                return
=======
        tool = self.gcmd_tool(gcmd, self.detected_tool)
        was_error  = self.status == STATUS_ERROR
>>>>>>> a85befe6eab3ab4da6a1de283d80b69f64b8dee7
        self.initialize(tool)
        if was_error and gcmd.get_int("RECOVER", default=0) == 1:
            if not tool:
                raise gcmd.error("Cannot recover, no tool")
            self._recover_position(gcmd, tool)

    cmd_SELECT_TOOL_help = 'Select active tool'
    def cmd_SELECT_TOOL(self, gcmd):
        tool_name = gcmd.get('TOOL', None)
        if tool_name:
            tool = self.printer.lookup_object(tool_name)
            if not tool:
                self._report_nonfatal(gcmd, "Select tool: TOOL=%s not found" % (tool_name))
                self._pause_print()
                return
            restore_axis = gcmd.get('RESTORE_AXIS', tool.t_command_restore_axis)
            self.select_tool(gcmd, tool, restore_axis)
            return
        tool_nr = gcmd.get_int('T', None)
        if tool_nr is not None:
            tool = self.lookup_tool(tool_nr)
            if not tool:
                self._report_nonfatal(gcmd, "Select tool: T%d not found" % (tool_nr))
                self._pause_print()
                return
            restore_axis = gcmd.get('RESTORE_AXIS', tool.t_command_restore_axis)
            self.select_tool(gcmd, tool, restore_axis)
            return
        self._report_nonfatal(gcmd, "Select tool: Either TOOL or T needs to be specified")
        self._pause_print()

    cmd_SET_TOOL_TEMPERATURE_help = 'Set temperature for tool'
    def cmd_SET_TOOL_TEMPERATURE(self, gcmd):
        temp = gcmd.get_float('TARGET', 0.)
        wait = gcmd.get_int('WAIT', 0) == 1
        tool = self._get_tool_from_gcmd(gcmd)
        if not tool:
            return
        if not tool.extruder:
            self._report_nonfatal(gcmd,
                "SET_TOOL_TEMPERATURE: No extruder specified for tool %s" % (tool.name))
            return
        heaters = self.printer.lookup_object('heaters')
        heaters.set_temperature(tool.extruder.get_heater(), temp, wait)

    def _get_tool_from_gcmd(self, gcmd):
        tool_name = gcmd.get('TOOL', None)
        tool_nr = gcmd.get_int('T', None)
        if tool_name:
            tool = self.printer.lookup_object(tool_name)
        elif tool_nr is not None:
            tool = self.lookup_tool(tool_nr)
            if not tool:
                self._report_nonfatal(gcmd, "SET_TOOL_TEMPERATURE: T%d not found" % (tool_nr))
                return None
        else:
            tool = self.active_tool
            if not tool:
                self._report_nonfatal(gcmd,
                    "SET_TOOL_TEMPERATURE: No tool specified and no active tool")
                return None
        return tool

    cmd_SELECT_TOOL_ERROR_help = "Abort tool change and mark the active toolchanger as failed"
    def cmd_SELECT_TOOL_ERROR(self, gcmd):
        if self.status != STATUS_CHANGING and self.status != STATUS_INITIALIZING:
            gcmd.respond_info('SELECT_TOOL_ERROR called while not selecting, doing nothing')
            return
<<<<<<< HEAD
        self._process_error(gcmd.get('MESSAGE', ''))
=======
        message = gcmd.get('MESSAGE', '')
        self._process_error(gcmd.error, message)
>>>>>>> a85befe6eab3ab4da6a1de283d80b69f64b8dee7

    cmd_UNSELECT_TOOL_help = "Unselect active tool without selecting a new one"
    def cmd_UNSELECT_TOOL(self, gcmd):
        if not self.active_tool:
            return
        restore_axis = gcmd.get('RESTORE_AXIS',
                                self.active_tool.t_command_restore_axis)
        self.select_tool(gcmd, None, restore_axis)

    cmd_RESET_TOOLCHANGER_STATUS_help = "Reset toolchanger from ERROR to READY state (for print recovery)"
    def cmd_RESET_TOOLCHANGER_STATUS(self, gcmd):
        """Reset toolchanger from ERROR back to READY."""
        if self.status != STATUS_ERROR:
            gcmd.respond_info("Toolchanger status is %s, not ERROR. No reset needed." % self.status)
            return

        if not self.active_tool:
            gcmd.respond_info("No active tool. Use INITIALIZE_TOOLCHANGER first.")
            return

        if self.has_detection:
            try:
                toolhead = self.printer.lookup_object('toolhead')
                toolhead.wait_moves()
                actual = self.detected_tool
                if actual != self.active_tool:
                    self._report_nonfatal(
                        gcmd,
                        "Tool mismatch: Expected %s but detected %s. Fix tool position first!" %
                        (self.active_tool.name if self.active_tool else "None",
                         actual.name if actual else "None"))
                    return
            except Exception as e:
                self._report_nonfatal(gcmd, "Tool detection failed: %s" % str(e))
                return

        old_status = self.status
        self.status = STATUS_READY
        self.error_message = ''
        gcmd.respond_info("✅ Toolchanger status reset: %s → %s" % (old_status, self.status))
        gcmd.respond_info("Active tool: %s (T%d)" % (self.active_tool.name, self.active_tool.tool_number))
        gcmd.respond_info("You can now RESUME the print!")

    cmd_SET_GCODE_OFFSET_help = "Overrides default SET_GCODE_OFFSET to handle global baby-stepping"
    def cmd_SET_GCODE_OFFSET(self, gcmd):
        z_adjust = gcmd.get_float('Z_ADJUST', None)
        if z_adjust is not None:
            self._handle_babystep(z_adjust)
        self.base_set_gcode_offset(gcmd)

    def cmd_RESET_INITIAL_TOOL(self, gcmd):
        """Resets the initial tool so another one can be used as reference."""
        if hasattr(self, 'initial_tool'):
            old_initial = self.initial_tool.name if self.initial_tool else "None"
            self.initial_tool = None
            try:
                tools_calibrate = self.printer.lookup_object('tools_calibrate')
                if hasattr(tools_calibrate, 'initial_tool'):
                    tools_calibrate.initial_tool = None
                    tools_calibrate.initial_location = None
                    self.gcode.respond_info("Reset: Initial tool in tools_calibrate")
            except self.printer.config_error:
                self.gcode.respond_info("Note: tools_calibrate object was not found")

            self.gcode.respond_info(f"Initial tool reset. Previous initial tool was: {old_initial}")
        else:
            self.gcode.respond_info("No initial tool available to reset.")

    cmd_RELOAD_TOOL_OFFSETS_help = "Reload tool offsets from config for a new initial tool"
    def cmd_RELOAD_TOOL_OFFSETS(self, gcmd):
        """Reload offsets from config into tool objects based on new initial tool."""
        new_initial_num = gcmd.get_int('TOOL', None)
        if new_initial_num is None:
            self._report_nonfatal(gcmd, "RELOAD_TOOL_OFFSETS: Please specify TOOL=<number>")
            return
        
        # Get the new initial tool object
        new_initial = self.lookup_tool(new_initial_num)
        if not new_initial:
            self._report_nonfatal(gcmd, f"RELOAD_TOOL_OFFSETS: Tool T{new_initial_num} not found")
            return
        
        # The offsets should already be loaded from config by tool.py during startup
        # They are stored in printer.cfg under [tool T<num>] section
        # Just verify they exist
        if not hasattr(new_initial, 'xy_offsets') or not hasattr(new_initial, 'z_offsets'):
            self._report_nonfatal(gcmd, f"RELOAD_TOOL_OFFSETS: Tool T{new_initial_num} has no offset data")
            return
        
        loaded_count = len(new_initial.xy_offsets)
        
        # Report what offsets are available (dynamically sized)
        max_tool_count = self.params.get('max_tool_count', 6)
        if loaded_count > 0:
            self.gcode.respond_info(f"Offsets for T{new_initial_num} (as initial tool, other tools are relative to it):")
            for i in range(max_tool_count):
                if i == new_initial_num:
                    continue
                
                # Report XY offsets
                if i in new_initial.xy_offsets:
                    x_off, y_off = new_initial.xy_offsets[i]
                    self.gcode.respond_info(f"  T{i} XY: X={x_off:.6f}, Y={y_off:.6f}")
                
                # Report Z offsets
                if i in new_initial.z_offsets:
                    z_off = new_initial.z_offsets[i]
                    self.gcode.respond_info(f"  T{i} Z: {z_off:.6f}")
        else:
            self.gcode.respond_info(f"No offsets found for T{new_initial_num}. This may be the first calibration.")
        
        # Update the initial_tool reference - offsets are already loaded
        self.initial_tool = new_initial
        try:
            tools_calibrate = self.printer.lookup_object('tools_calibrate')
            if hasattr(tools_calibrate, 'initial_tool'):
                tools_calibrate.initial_tool = new_initial
                self.gcode.respond_info("Updated initial_tool in tools_calibrate")
        except self.printer.config_error:
            pass
        
        self.gcode.respond_info(f"✅ Set T{new_initial_num} as new initial tool ({loaded_count} offsets available)")

    def cmd_SET_CALIBRATION_MODE(self, gcmd):
        """Enable or disable calibration mode (disables Z-offset application)."""
        enable = gcmd.get_int('ENABLE', 0)
        self.calibration_mode = (enable == 1)
        if self.calibration_mode:
            self.gcode.respond_info("⚙️ Calibration mode ENABLED - Z-offsets will NOT be applied during tool changes")
        else:
            self.gcode.respond_info("✅ Calibration mode DISABLED - normal Z-offset behavior restored")

    cmd_TEST_TOOL_DOCKING_help = "Unselect active tool and select it again"
    def cmd_TEST_TOOL_DOCKING(self, gcmd):
        if not self.active_tool:
            self._report_nonfatal(gcmd, "Cannot test tool, no active tool")
            return
        restore_axis = gcmd.get('RESTORE_AXIS',
                                self.active_tool.t_command_restore_axis)
        self.test_tool_selection(gcmd, restore_axis)

    # ==============================================================================
    #                                 Main Flows
    # ==============================================================================

    def initialize(self, select_tool=None):
        if self.status == STATUS_CHANGING:
            # Non-fatal instead of raising
            self._report_nonfatal(None, 'Cannot initialize while changing tools')
            return

        should_run_initialize = self.status != STATUS_INITIALIZING
        extra_context = {
            'dropoff_tool': None,
            'pickup_tool': select_tool.name if select_tool else None,
        }

        try:
            if should_run_initialize:
                self.status = STATUS_INITIALIZING
                self.run_gcode('initialize_gcode', self.initialize_gcode, extra_context)

<<<<<<< HEAD
            if select_tool:
                try:
                    self._configure_toolhead_for_tool(select_tool)
                    self.run_gcode('after_change_gcode', select_tool.after_change_gcode, extra_context)
                    if self.initial_tool and select_tool == self.initial_tool:
                        self.gcode.run_script_from_command("SET_GCODE_OFFSET X=0 Y=0")
                except Exception as e:
                    self.gcode.respond_info(f"Warning: Error during tool initialization: {str(e)}")
                    self._process_error(str(e))
                    return
=======
        if select_tool or self.has_detection:
            self._configure_toolhead_for_tool(select_tool)
            if select_tool:
                self.run_gcode('after_change_gcode', select_tool.after_change_gcode, extra_context)
                self._set_tool_gcode_offset(select_tool, 0.0)
            if self.require_tool_present and self.active_tool is None:
                raise self.gcode.error(
                    '%s failed to initialize, require_tool_present set and no tool present after initialization' % (
                        self.name,))
>>>>>>> a85befe6eab3ab4da6a1de283d80b69f64b8dee7

            if should_run_initialize:
                if self.status == STATUS_INITIALIZING:
                    self.status = STATUS_READY
                    self.gcode.respond_info('%s initialized, active %s' %
                                            (self.name,
                                             self.active_tool.name if self.active_tool else None))
                else:
                    self.gcode.respond_info('%s failed to initialize, error: %s' %
                                            (self.name, self.error_message))
        except Exception as e:
            self.gcode.respond_info(f"Warning: Toolchanger initialization failed: {str(e)}")
            self._process_error(str(e))

    def select_tool(self, gcmd, tool, restore_axis):
        if self.status == STATUS_UNINITALIZED and self.initialize_on == INIT_FIRST_USE:
            self.initialize(self.detected_tool)
        if self.status != STATUS_READY:
<<<<<<< HEAD
            self._report_nonfatal(gcmd, "Cannot select tool, toolchanger status is %s" % (self.status,))
            self._pause_print()
            return

        # set initial tool if not yet set
        if not hasattr(self, 'initial_tool'):
            self.initial_tool = None
        if self.initial_tool is None and tool is not None:
            self.initial_tool = tool
            self.gcode.respond_info("Setting T%d as initial tool for Z-offset reference" % tool.tool_number)
            try:
                globals_macro = self.printer.lookup_object('gcode_macro globals')
                global_offset = globals_macro.variables.get('global_z_offset', 0.06)
                tool_var_name = 't%d_z_offset' % tool.tool_number
                if hasattr(globals_macro.variables, tool_var_name):
                    globals_macro.variables[tool_var_name] = global_offset
                self.gcode.run_script_from_command('SET_GCODE_OFFSET Z=%.3f ABSOLUTE=1' % (global_offset,))
            except Exception:
                self.gcode.run_script_from_command('SET_GCODE_OFFSET Z=0.06 ABSOLUTE=1')

        if self.active_tool == tool:
            # ABER: Global Z-Offset trotzdem setzen wenn es das Initial-Tool ist!
            if tool and self.initial_tool:
                try:
                    globals_macro = self.printer.lookup_object('gcode_macro globals')
                    global_offset = globals_macro.variables.get('global_z_offset', 0.06)
                    
                    if tool == self.initial_tool:
                        self.gcode.run_script_from_command('SET_GCODE_OFFSET Z=%.3f ABSOLUTE=1' % (global_offset,))
                        self.gcode.respond_info("Applied global Z-offset %.3f for initial tool (already active)" % global_offset)
                except Exception as e:
                    self.gcode.respond_info("Warning: Could not set Z-offset: %s" % str(e))
            
            gcmd.respond_info('Tool %s already selected' % (tool.name if tool else None))
            return

        # Save current offsets before the change
        current_offsets = self.gcode_move.get_status()['homing_origin']
        self.gcode.respond_info(
            "Saving current offsets before tool change: X=%.3f, Y=%.3f, Z=%.3f" %
            (current_offsets[0], current_offsets[1], current_offsets[2]))

        # previous tool Z-offset (relative) if available
        current_z_offset = 0.0
        if self.active_tool and self.initial_tool and hasattr(self.initial_tool, 'z_offsets'):
            current_z_offset = self.initial_tool.z_offsets.get(self.active_tool.tool_number, 0.0)

        if not self.ensure_homed(gcmd):
=======
            raise gcmd.error(
                "Cannot select tool, toolchanger status is %s, reason: %s" % (self.status, self.error_message))

        if self.active_tool == tool:
            gcmd.respond_info(
                'Tool %s already selected' % tool.name if tool else None)
>>>>>>> a85befe6eab3ab4da6a1de283d80b69f64b8dee7
            return
        this_change_id = self.next_change_id
        self.next_change_id += 1
        self.current_change_id = this_change_id

<<<<<<< HEAD
        self.status = STATUS_CHANGING
        toolhead_status = self.gcode_move.get_status()
        toolhead_position = toolhead_status['position']
        gcode_position = toolhead_status['gcode_position']
        extra_z_offset = toolhead_position[2] - gcode_position[2] - (current_z_offset if self.active_tool else 0.0)
=======
        try:
            self.ensure_homed(gcmd)
            self.status = STATUS_CHANGING
>>>>>>> a85befe6eab3ab4da6a1de283d80b69f64b8dee7

            # What is going on here:
            #  - toolhead position - the position of the toolhead mount relative to homing sensors.
            #  - gcode position - the position of the nozzle, relative to the bed;
            #      since each tool has a slightly different geometry, each tool has a set of gcode offsets that determine the delta.
            # Normally gcode commands use gcode position, but that can mean different toolhead positions depending on
            # which tool is mounted, making tool changes unreliable.
            # To solve that, during toolchange Gcode offsets are set to zero and the gcode moves directly work with toolhead position.
            # And nozzle location will deviate for each tool.
            #
            # To restore the new tool's nozzle to where the previous tool left off, the restore position is manually computed in the code below.
            gcode_status = self.gcode_move.get_status()
            gcode_position = gcode_status['gcode_position']
            current_z_offset = gcode_status['homing_origin'][2] # Current Z offset applied; Contains both the tool offset plus any manual changes by the user.
            extra_z_offset = current_z_offset - (self.active_tool.gcode_z_offset if self.active_tool else 0.0)

            self.last_change_gcode_position = gcode_position
            self.last_change_start_position = self._position_to_xyz(gcode_position, 'xyz')
            self.last_change_restore_position = self._position_to_xyz(gcode_position, restore_axis)
            self.last_change_restore_axis = restore_axis
            self.last_change_extra_z_offset = extra_z_offset
            self.last_change_pickup_tool = tool

            extra_context = {
                'dropoff_tool': self.active_tool.name if self.active_tool else None,
                'pickup_tool': tool.name if tool else None,
                'start_position': self._position_with_tool_offset(gcode_position, 'xyz', tool, extra_z_offset),
                'restore_position': self._position_with_tool_offset(gcode_position, restore_axis, tool, extra_z_offset),
            }

            self.gcode.run_script_from_command("SAVE_GCODE_STATE NAME=_toolchange_state")

            before_change_gcode = self.active_tool.before_change_gcode if self.active_tool else self.default_before_change_gcode
            self.run_gcode('before_change_gcode', before_change_gcode, extra_context)
            self.gcode.run_script_from_command("SET_GCODE_OFFSET X=0.0 Y=0.0 Z=0.0")

            if self.active_tool:
                self.run_gcode('tool.dropoff_gcode',
                               self.active_tool.dropoff_gcode, extra_context)

            self._configure_toolhead_for_tool(tool)
            if tool is not None:
                self.run_gcode('tool.pickup_gcode',
                               tool.pickup_gcode, extra_context)
                if self.has_detection and self.verify_tool_pickup:
                    self.validate_detected_tool(tool, respond_info=gcmd.respond_info, raise_error=gcmd.error)
                self.run_gcode('after_change_gcode',
                               tool.after_change_gcode, extra_context)

            self._restore_axis(gcode_position, restore_axis, tool)

            self.gcode.run_script_from_command(
                "RESTORE_GCODE_STATE NAME=_toolchange_state MOVE=0")
            # Restore state sets old gcode offsets, fix that.
            if tool is not None:
                self._set_tool_gcode_offset(tool, extra_z_offset)

            self.status = STATUS_READY
            if tool:
                gcmd.respond_info(
                    'Selected tool %s (%s)' % (str(tool.tool_number), tool.name))
            else:
                gcmd.respond_info('Tool unselected')
            self.current_change_id = -1
        except gcmd.error:
            if self.status == STATUS_ERROR:
                # The error handling did happen, we can continue
                pass
            else:
                # This was not handled, abort.
                self.current_change_id = -1
                raise

    def _process_error(self, raise_error, message):
        self.status = STATUS_ERROR
        self.error_message = message
        is_inside_toolchange = self.current_change_id != -1

        self.current_change_id = -1
        if self.error_gcode:
            extra_context = {}
            if is_inside_toolchange:
                extra_context = {
                    'start_position': self.last_change_start_position,
                    'restore_position': self.last_change_restore_position,
                    'pickup_tool': self.last_change_pickup_tool,
                }
                # Restore gcode state, but do not move. Prepare for error_gcode to run pause and capture the state for resume.
                self.gcode.run_script_from_command(
                    "RESTORE_GCODE_STATE NAME=_toolchange_state MOVE=0")
            self.run_gcode('error_gcode', self.error_gcode, extra_context)
            if is_inside_toolchange:
                # HACKY HACKY HACKY
                # Manually transfer over before toolchange position to paused gcode state, Restore/Save looses that.
                pause_state = self.gcode_move.saved_states.get('PAUSE_STATE', None)
                if pause_state and self.last_change_pickup_tool:
                    pause_state['last_position'] = [self.last_change_gcode_position[0] + self.last_change_pickup_tool.gcode_x_offset,
                                                    self.last_change_gcode_position[1] + self.last_change_pickup_tool.gcode_y_offset,
                                                    self.last_change_gcode_position[2] + self.last_change_pickup_tool.gcode_z_offset + self.last_change_extra_z_offset,
                                                    self.last_change_gcode_position[3]]

        # Bail out rest of the gcmd execution.
        if raise_error:
            raise raise_error(message)

    def _recover_position(self, gcmd, tool):
        extra_context = {
            'pickup_tool': tool.name if tool else None,
<<<<<<< HEAD
            'restore_position': self._position_with_tool_offset(gcode_position, restore_axis, tool),
            'start_position': self._position_with_tool_offset(gcode_position, 'xyz', tool)
        }

        self.gcode.run_script_from_command("SAVE_GCODE_STATE NAME=_toolchange_state")

        # Zero offsets before the change
        self.gcode.run_script_from_command("SET_GCODE_OFFSET X=0 Y=0 Z=0 ABSOLUTE=1")
        self.gcode.respond_info("Reset offsets to zero for tool change")

        before_change_gcode = self.active_tool.before_change_gcode if self.active_tool else self.default_before_change_gcode
        self.run_gcode('before_change_gcode', before_change_gcode, extra_context)

        # --- DROPOFF ---
        if self.active_tool:
            self.run_gcode('dropoff_gcode', self.active_tool.dropoff_gcode, extra_context)
            if self.status == STATUS_ERROR:
                self._pause_print()
                self.gcode.run_script_from_command("RESTORE_GCODE_STATE NAME=_toolchange_state MOVE=0")
                self.status = STATUS_READY
                return

        # --- SWITCH TOOLHEAD CONTEXT ---
        self._configure_toolhead_for_tool(tool)

        # --- PICKUP (STAGE-AWARE) ---
        if tool is not None:
            # Check if tool has stage-based templates
            has_stage1 = hasattr(tool, 'pickup_gcode_stage1') and tool.pickup_gcode_stage1 is not None
            has_stage2 = hasattr(tool, 'pickup_gcode_stage2') and tool.pickup_gcode_stage2 is not None
            
            if has_stage1:
                # Stage 1: Move to detection point
                self.run_gcode('pickup_gcode_stage1', tool.pickup_gcode_stage1, extra_context)
                if self.status == STATUS_ERROR:
                    self._pause_print()
                    self.gcode.run_script_from_command("RESTORE_GCODE_STATE NAME=_toolchange_state MOVE=0")
                    # Keep ERROR status - will be reset by RESET_TOOLCHANGER_STATUS
                    return
                
                # Verify tool detected
                if self.has_detection and self.verify_tool_pickup:
                    ok = self._wait_for_detection_state(tool, expect_present=True, retries=10, delay=0.1)
                    if not ok:
                        self._flush_motion_and_freeze_position()
                        safe_y = self.params.get('params_safe_y', 105)
                        
                        # Get target temperature for recovery instructions
                        target_temp = 200  # Default fallback
                        if tool.extruder:
                            try:
                                target_temp = int(self.printer.lookup_object(tool.extruder_name).get_heater().target)
                                if target_temp == 0:
                                    target_temp = 200  # Use default if heater is off
                            except Exception:
                                pass
                        
                        self.gcode.respond_info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                        self.gcode.respond_info("📋 RECOVERY STEPS:")
                        self.gcode.respond_info("1. Manually attach T%d to the shuttle" % tool.tool_number)
                        self.gcode.respond_info("2. Heat tool: M109 T%d S%d" % (tool.tool_number, target_temp))
                        self.gcode.respond_info("3. Run: G0 Y%d F6000" % safe_y)
                        self.gcode.respond_info("4. Run: RESUME")
                        self.gcode.respond_info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                        self._process_error("Tool pickup verification failed (stage1)")
                        self._pause_print()
                        self.gcode.run_script_from_command("RESTORE_GCODE_STATE NAME=_toolchange_state MOVE=0")
                        # Keep ERROR status - will be reset by RESET_TOOLCHANGER_STATUS
                        return
                    
                    # Double-check: correct tool?
                    self.note_detect_change(tool)
                    if self.detected_tool != tool:
                        self._flush_motion_and_freeze_position()
                        self._process_error(
                            f"Tool mismatch: expected {tool.name}, detected {self.detected_tool.name if self.detected_tool else 'None'}"
                        )
                        self._pause_print()
                        self.gcode.run_script_from_command("RESTORE_GCODE_STATE NAME=_toolchange_state MOVE=0")
                        # Keep ERROR status - will be reset by RESET_TOOLCHANGER_STATUS
                        return
                
                # Stage 2: Complete pickup (only if stage1 succeeded)
                if has_stage2:
                    self.run_gcode('pickup_gcode_stage2', tool.pickup_gcode_stage2, extra_context)
                    if self.status == STATUS_ERROR:
                        self._pause_print()
                        self.gcode.run_script_from_command("RESTORE_GCODE_STATE NAME=_toolchange_state MOVE=0")
                        # Keep ERROR status - will be reset by RESET_TOOLCHANGER_STATUS
                        return
            else:
                # Legacy single-stage pickup
                self.run_gcode('pickup_gcode', tool.pickup_gcode, extra_context)
                if self.status == STATUS_ERROR:
                    self._pause_print()
                    self.gcode.run_script_from_command("RESTORE_GCODE_STATE NAME=_toolchange_state MOVE=0")
                    # Keep ERROR status - will be reset by RESET_TOOLCHANGER_STATUS
                    return

            # Restore state (this will restore old offsets - which were 0)
            self.gcode.run_script_from_command("RESTORE_GCODE_STATE NAME=_toolchange_state MOVE=0")

            # NOW set the correct Z / XY offsets AFTER RESTORE_GCODE_STATE
            try:
                globals_macro = self.printer.lookup_object('gcode_macro globals')
                global_offset = globals_macro.variables.get('global_z_offset', 0.06)

                # During calibration mode, do NOT apply Z-offsets (they are being measured)
                if self.calibration_mode:
                    self.gcode.run_script_from_command('SET_GCODE_OFFSET Z=0 ABSOLUTE=1')
                    self.gcode.respond_info("⚙️ Calibration mode: Z-offset set to 0 for T%d" % tool.tool_number)
                elif tool == self.initial_tool:
                    total_offset = global_offset
                    self.gcode.respond_info("Restored initial tool (%s) with global offset: %f" %
                                            (tool.tool_number, global_offset))
                    self.gcode.run_script_from_command('SET_GCODE_OFFSET Z=%.3f ABSOLUTE=1' % (total_offset,))
                else:
                    z_offset = self.initial_tool.z_offsets.get(tool.tool_number, 0.0) if self.initial_tool else 0.0
                    total_offset = z_offset + global_offset
                    self.gcode.respond_info("Setting Z-offset for T%d: tool=%f, global=%f, total=%f" %
                                            (tool.tool_number, z_offset, global_offset, total_offset))
                    self.gcode.run_script_from_command('SET_GCODE_OFFSET Z=%.3f ABSOLUTE=1' % (total_offset,))

                if tool == self.initial_tool:
                    self.gcode.run_script_from_command("SET_GCODE_OFFSET X=0 Y=0 ABSOLUTE=1")
                    self.gcode.respond_info("Initial tool setting reference XY-offset to 0")
                elif (self.initial_tool and hasattr(self.initial_tool, 'xy_offsets') and
                      tool.tool_number in self.initial_tool.xy_offsets):
                    x_offset, y_offset = self.initial_tool.xy_offsets[tool.tool_number]
                    self.gcode.run_script_from_command(
                        f"SET_GCODE_OFFSET X={x_offset:.6f} Y={y_offset:.6f} ABSOLUTE=1")
                    self.gcode.respond_info(
                        f"Setting XY-offset for T{tool.tool_number}: X={x_offset:.6f}, Y={y_offset:.6f}")
            except Exception as e:
                self.gcode.respond_info("Error setting offset: %s" % str(e))
            
            # After-change - now includes safe_y move and Z-restore with ROUNDED_G0
            self.run_gcode('after_change_gcode', tool.after_change_gcode, extra_context)
            if self.status == STATUS_ERROR:
                self._pause_print()
                self.gcode.run_script_from_command("RESTORE_GCODE_STATE NAME=_toolchange_state MOVE=0")
                # Keep ERROR status - will be reset by RESET_TOOLCHANGER_STATUS
                return

        self.status = STATUS_READY
        if tool:
            gcmd.respond_info('Selected tool %s (%s)' % (str(tool.tool_number), tool.name))
        else:
            gcmd.respond_info('Tool unselected')
=======
            'start_position': self.last_change_start_position,
            'restore_position': self.last_change_restore_position,
        }
        self.run_gcode('recover_gcode', tool.recover_gcode, extra_context)
        self._restore_axis(self.last_change_gcode_position, self.last_change_restore_axis, tool)
        self.gcode.run_script_from_command(
            "RESTORE_GCODE_STATE NAME=_toolchange_state MOVE=0")
        # Restore state sets old gcode offsets, fix that.
        self._set_tool_gcode_offset(tool, self.last_change_extra_z_offset)
>>>>>>> a85befe6eab3ab4da6a1de283d80b69f64b8dee7

    def test_tool_selection(self, gcmd, restore_axis):
        if self.status != STATUS_READY:
            self._report_nonfatal(gcmd, "Cannot test tool, toolchanger status is %s" % (self.status,))
            return
        tool = self.active_tool
        if not tool:
            self._report_nonfatal(gcmd, "Cannot test tool, no active tool")
            return

        self.status = STATUS_CHANGING
        gcode_position = self.gcode_move.get_status()['gcode_position']
        extra_context = {
            'dropoff_tool': self.active_tool.name if self.active_tool else None,
            'pickup_tool': tool.name if tool else None,
            'restore_position': self._position_with_tool_offset(gcode_position, restore_axis, None),
            'start_position': self._position_with_tool_offset(gcode_position, 'xyz', tool)
        }

        self.gcode.run_script_from_command("SET_GCODE_OFFSET X=0.0 Y=0.0 Z=0.0")
        
        # Drop current tool
        self.run_gcode('dropoff_gcode', tool.dropoff_gcode, extra_context)
        if self.status == STATUS_ERROR:
            self._pause_print()
            self.gcode.respond_info("⚠️ Dropoff failed during test")
            # Keep ERROR status - will be reset by RESET_TOOLCHANGER_STATUS
            return
        
        # Pickup tool
        self.run_gcode('pickup_gcode', tool.pickup_gcode, extra_context)
        if self.status == STATUS_ERROR:
            self._pause_print()
            self.gcode.respond_info("⚠️ Pickup failed during test")
            # Keep ERROR status - will be reset by RESET_TOOLCHANGER_STATUS
            return
        
        # Ensure toolhead is stationary before restoring
        toolhead = self.printer.lookup_object('toolhead')
        toolhead.wait_moves()
        # Restore axis
        self._restore_axis(gcode_position, restore_axis, None)
        # Reset status
        self.status = STATUS_READY
        gcmd.respond_info('Tool testing done')

    # ==============================================================================
    #                         Detection & Verification
    # ==============================================================================

    def lookup_tool(self, number):
        return self.tools.get(number, None)

    def get_selected_tool(self):
        return self.active_tool

    def note_detect_change(self, tool):
        detected = None
        detected_names = []
        for tool in self.tools.values():
            if tool.detect_state == DETECT_PRESENT:
                detected = tool
<<<<<<< HEAD
                detected_count += 1
        if detected_count > 1:
=======
                detected_names.append(tool.name)
        if len(detected_names) > 1:
            self.gcode.respond_info("Multiple tools detected: %s" % (detected_names,))
>>>>>>> a85befe6eab3ab4da6a1de283d80b69f64b8dee7
            detected = None
        self.detected_tool = detected

    def require_detected_tool(self, respond_info):
        if self.detected_tool is not None:
            return self.detected_tool
        detected = None
        detected_names = []
        for tool in self.tools.values():
            if tool.detect_state == DETECT_PRESENT:
                detected = tool
                detected_names.append(tool.name)
        if len(detected_names) > 1:
<<<<<<< HEAD
            self._report_nonfatal(gcmd, "Multiple tools detected: %s" % detected_names)
            self._pause_print()
            return None
        if detected is None:
            self._report_nonfatal(gcmd, "No tool detected")
            self._pause_print()
            return None
        return detected

    def validate_detected_tool(self, expected, gcmd):
        actual = self.require_detected_tool(gcmd)
        toolhead = self.printer.lookup_object('toolhead')

        def _flush_motion():
            # Warte auf laufende Moves, friere aktuelle Position ein
            self.gcode.run_script_from_command("M400")
            self.gcode.run_script_from_command(
                "SET_KINEMATIC_POSITION X={x:.3f} Y={y:.3f} Z={z:.3f}".format(
                    x=toolhead.position.x,
                    y=toolhead.position.y,
                    z=toolhead.position.z
                )
            )
            self.gcode.respond_info("⚠️ Planner flushed – queued moves canceled.")

        # --- No tool detected ---
        if not actual:
            _flush_motion()
            self._process_error("Tool detection failed: No tool detected")
            self._pause_print()
            self.status = "error"
            return False

        # --- Wrong tool detected ---
=======
            respond_info("Multiple tools detected: %s" % (detected_names,))
        if detected is None:
            respond_info("No tool detected")
        return detected

    def validate_detected_tool(self, expected, respond_info, raise_error):
        actual = self.require_detected_tool(respond_info)
>>>>>>> a85befe6eab3ab4da6a1de283d80b69f64b8dee7
        if actual != expected:
            _flush_motion()
            expected_name = expected.name if expected else "None"
            actual_name = actual.name if actual else "None"
<<<<<<< HEAD
            self._process_error(
                f"Tool detection failed: Expected {expected_name} but detected {actual_name}"
            )
            self._pause_print()
            self.status = "error"
            return False

        return True


    def cmd_VERIFY_TOOL_DETECTED(self, gcmd):
        """Compatibility for old templates: verifies PRESENCE softly, without shutdown."""
        expected = self._gcmd_tool(gcmd, self.active_tool)
        if not expected or not self.has_detection:
            return
        present = self._wait_for_detection_state(expected, expect_present=True, retries=10, delay=0.1)
        if not present:
            self._flush_motion_and_freeze_position()
            
            # Clear user instructions - NO automatic move to safe_y!
            safe_y = self.params.get('params_safe_y', 105)
            
            # Get target temperature for recovery instructions
            target_temp = 200  # Default fallback
            if expected.extruder:
                try:
                    target_temp = int(self.printer.lookup_object(expected.extruder_name).get_heater().target)
                    if target_temp == 0:
                        target_temp = 200  # Use default if heater is off
                except Exception:
                    pass
            
            self.gcode.respond_info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            self.gcode.respond_info("📋 RECOVERY STEPS:")
            self.gcode.respond_info("1. Manually attach T%d to the shuttle" % expected.tool_number)
            self.gcode.respond_info("2. Heat tool: M109 T%d S%d" % (expected.tool_number, target_temp))
            self.gcode.respond_info("3. Run: G0 Y%d F6000" % safe_y)
            self.gcode.respond_info("4. Run: RESUME")
            self.gcode.respond_info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
            self._process_error("Tool detection failed (compat VERIFY)")
            self._pause_print()

    # ==============================================================================
    #                          Kinematics & Offsets
    # ==============================================================================
=======
            message = "Expected tool %s but active is %s" % (expected_name, actual_name)
            self._process_error(raise_error, message)

    def cmd_VERIFY_TOOL_DETECTED(self, gcmd):
        self._ensure_toolchanger_ready(gcmd)
        expected = self.gcmd_tool(gcmd, self.active_tool)
        if not self.has_detection:
            return
        toolhead = self.printer.lookup_object('toolhead')
        reactor = self.printer.get_reactor()
        if gcmd.get_int("ASYNC", 0) == 1:
            if self.error_gcode is None:
                raise gcmd.error("VERIFY_TOOL_DETECTED ASYNC=1 needs error_gcode to be defined")
            def timer_handler(reactor_time) :
                self.validate_detected_tool(expected, respond_info=gcmd.respond_info, raise_error=None)
                return reactor.NEVER
            if self.validate_tool_timer:
                reactor.unregister_timer(self.validate_tool_timer)
            self.validate_tool_timer = toolhead.register_lookahead_callback(lambda print_time:
                                                                            reactor.register_timer(timer_handler, reactor.monotonic() + 0.2 + max(0.0, print_time - toolhead.mcu.estimated_print_time(reactor.monotonic())) ))
        else:
            toolhead.wait_moves()
            # Wait some more to allow tool sensors to update
            reactor.pause(reactor.monotonic() + 0.2)
            self.validate_detected_tool(expected, respond_info=gcmd.respond_info, raise_error=gcmd.error)
>>>>>>> a85befe6eab3ab4da6a1de283d80b69f64b8dee7

    def _configure_toolhead_for_tool(self, tool):
        if self.active_tool:
            self.active_tool.deactivate()
        self.active_tool = tool
        if self.active_tool:
            self.active_tool.activate()

<<<<<<< HEAD
    def _position_with_tool_offset(self, position, axis, tool):
        """Compute position with tool offsets applied."""
=======
    def _set_tool_gcode_offset(self, tool, extra_z_offset):
        if tool is None:
            return
        if tool.gcode_x_offset is None and tool.gcode_y_offset is None and tool.gcode_z_offset is None:
            return
        cmd = 'SET_GCODE_OFFSET'
        if tool.gcode_x_offset is not None:
            cmd += ' X=%f' % (tool.gcode_x_offset,)
        if tool.gcode_y_offset is not None:
            cmd += ' Y=%f' % (tool.gcode_y_offset,)
        if tool.gcode_z_offset is not None:
            cmd += ' Z=%f' % (tool.gcode_z_offset + extra_z_offset,)
        self.gcode.run_script_from_command(cmd)
        mesh = self.printer.lookup_object('bed_mesh', default=None)
        if mesh and mesh.get_mesh():
            self.gcode.run_script_from_command(
                'BED_MESH_OFFSET X=%.6f Y=%.6f ZFADE=%.6f' %
                (-tool.gcode_x_offset, -tool.gcode_y_offset,
                 -tool.gcode_z_offset))

    def _position_to_xyz(self, position, axis):
        result = {}
        for i in axis:
            index = XYZ_TO_INDEX[i]
            result[INDEX_TO_XYZ[index]] = position[index]
        return result

    def _position_with_tool_offset(self, position, axis, tool, extra_z_offset=0.0):
>>>>>>> a85befe6eab3ab4da6a1de283d80b69f64b8dee7
        result = {}
        for i in axis:
            index = XYZ_TO_INDEX[i]
            v = position[index]
            if tool and self.initial_tool:
                try:
                    if index < 2:  # X or Y
                        if tool != self.initial_tool and tool.tool_number in self.initial_tool.xy_offsets:
                            offset = self.initial_tool.xy_offsets[tool.tool_number][index]
                            v += offset
                    elif index == 2:  # Z
                        if tool == self.initial_tool:
                            globals_macro = self.printer.lookup_object('gcode_macro globals')
                            offset = globals_macro.variables.get('global_z_offset', 0.06)
                        else:
                            globals_macro = self.printer.lookup_object('gcode_macro globals')
                            global_offset = globals_macro.variables.get('global_z_offset', 0.06)
                            tool_offset = self.initial_tool.z_offsets.get(tool.tool_number, 0.0)
                            offset = tool_offset + global_offset
                        v += offset
                except Exception as e:
                    self.gcode.respond_info(f"Warning: Error calculating offset: {str(e)}")
            result[INDEX_TO_XYZ[index]] = v
        return result

    def _restore_axis(self, position, axis, tool):
        if not axis:
            return
        pos = self._position_with_tool_offset(position, axis, tool)
        self.gcode_move.cmd_G1(self.gcode.create_gcode_command("G0", "G0", pos))

    def run_gcode(self, name, template, extra_context):
        """Run a GCode template; never raise fatal errors."""
        current_status = self.status
        curtime = self.printer.get_reactor().monotonic()
<<<<<<< HEAD
        try:
            context = {
                **template.create_template_context(),
                'tool': self.active_tool.get_status(curtime) if self.active_tool else {},
                'toolchanger': self.get_status(curtime),
                **extra_context,
            }
            template.run_gcode_from_command(context)
        except Exception as e:
            # Non-fatal: record error and pause; do not raise
            self._process_error(f"Script running error in {name}: {e}")
            self._pause_print()
            return

    # ==============================================================================
    #                                 Parameters
    # ==============================================================================
=======
        context = {
            **template.create_template_context(),
            'tool': self.active_tool.get_status(
                curtime) if self.active_tool else {},
            'toolchanger': self.get_status(curtime),
            **extra_context,
        }
        template.run_gcode_from_command(context)
>>>>>>> a85befe6eab3ab4da6a1de283d80b69f64b8dee7

    def cmd_SET_TOOL_PARAMETER(self, gcmd):
        tool = self._get_tool_from_gcmd(gcmd)
        if not tool:
            return
        name = gcmd.get("PARAMETER")
        if name in tool.params and name not in tool.original_params:
            tool.original_params[name] = tool.params[name]
        try:
            value = ast.literal_eval(gcmd.get("VALUE"))
        except Exception:
            # accept raw string if not a literal
            value = gcmd.get("VALUE")
        tool.params[name] = value

    def cmd_RESET_TOOL_PARAMETER(self, gcmd):
        tool = self._get_tool_from_gcmd(gcmd)
        if not tool:
            return
        name = gcmd.get("PARAMETER")
        if name in tool.original_params:
            tool.params[name] = tool.original_params[name]

    def cmd_SAVE_TOOL_PARAMETER(self, gcmd):
        tool = self._get_tool_from_gcmd(gcmd)
        if not tool:
            return
        name = gcmd.get("PARAMETER")
        if name not in tool.params:
            self._report_nonfatal(gcmd, 'Tool does not have parameter %s' % (name))
            return
        configfile = self.printer.lookup_object('configfile')
        configfile.set(tool.name, name, tool.params[name])

    def ensure_homed(self, gcmd):
        """Ensure required axes are homed; optionally home, never raise."""
        if not self.uses_axis:
            return True

        toolhead = self.printer.lookup_object('toolhead')
        curtime = self.printer.get_reactor().monotonic()
        homed = toolhead.get_kinematics().get_status(curtime)['homed_axes']
        needs_homing = any(axis not in homed for axis in self.uses_axis)
        if not needs_homing:
            return True

        # Wait for current moves to finish
        toolhead.wait_moves()
        curtime = self.printer.get_reactor().monotonic()
        homed = toolhead.get_kinematics().get_status(curtime)['homed_axes']
        axis_to_home = list(filter(lambda a: a not in homed, self.uses_axis))
        if not axis_to_home:
            return True

        if self.on_axis_not_homed == ON_AXIS_NOT_HOMED_ABORT:
<<<<<<< HEAD
            self._report_nonfatal(
                gcmd,
                "Cannot perform toolchange, axis not homed. Required: %s, homed: %s" %
                (self.uses_axis, homed))
            self._pause_print()
            return False

        # Home the missing axes
=======
            raise gcmd.error(
                "Cannot perform toolchange, axis not homed. Required: %s, homed: %s" % (
                    self.uses_axis, homed))
        # Home the missing axis
>>>>>>> a85befe6eab3ab4da6a1de283d80b69f64b8dee7
        axis_str = " ".join(axis_to_home).upper()
        gcmd.respond_info('Homing %s before toolchange' % (axis_str,))
        self.gcode.run_script_from_command("G28 %s" % (axis_str,))

        # Verify again
        toolhead.wait_moves()
        curtime = self.printer.get_reactor().monotonic()
        homed = toolhead.get_kinematics().get_status(curtime)['homed_axes']
        axis_to_home = list(filter(lambda a: a not in homed, self.uses_axis))
        if axis_to_home:
            self._report_nonfatal(
                gcmd,
                "Cannot perform toolchange, required axis still not homed after homing move. Required: %s, homed: %s" %
                (self.uses_axis, homed))
            self._pause_print()
            return False
        return True

    # ==============================================================================
    #                              Parsing Helpers
    # ==============================================================================

    class sentinel:
        pass

    def _gcmd_tool(self, gcmd, default=sentinel):
        tool_name = gcmd.get('TOOL', None)
        tool_number = gcmd.get_int('T', None)
        tool = None
        if tool_name:
            tool = self.printer.lookup_object(tool_name)
        if tool_number is not None:
            tool = self.lookup_tool(tool_number)
            if not tool:
                self._report_nonfatal(gcmd, 'Tool #%d is not assigned' % (tool_number))
                return None
        if tool is None:
            if default == sentinel:
                self._report_nonfatal(gcmd, 'Missing TOOL=<name> or T=<number>')
                return None
            tool = default
        return tool

<<<<<<< HEAD
# ==============================================================================
#                                 Module Hooks
# ==============================================================================
=======
    def _ensure_toolchanger_ready(self, gcmd):
        if self.status not in [STATUS_READY, STATUS_CHANGING]:
            raise gcmd.error("VERIFY_TOOL_DETECTED: toolchanger not ready: status = %s", (self.status,))

class FanSwitcher:
    def __init__(self, toolchanger, config):
        self.toolchanger = toolchanger
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        self.config = config
        self.has_multi_fan = bool(config.get_prefix_sections('multi_fan'))
        self.has_printer_fan = bool(config.has_section('fan'))
        self.pending_speed = None
        self.active_fan = None
        self.transfer_fan_speed = toolchanger.transfer_fan_speed
        if self.has_printer_fan:
            raise config.error("Cannot use tool fans together with [fan], use [fan_generic] for tool fans.")
        if not self.has_multi_fan and not self.has_printer_fan:
            self.gcode.register_command("M106", self.cmd_M106)
            self.gcode.register_command("M107", self.cmd_M107)

    def activate_fan(self, fan):
        if self.has_multi_fan:
            # Legacy multi-fan support
            self.gcode.run_script_from_command("ACTIVATE_FAN FAN='%s'" % (fan.name,))
            return
        if self.active_fan == fan or not self.transfer_fan_speed:
            return

        speed_to_set = self.pending_speed
        if self.active_fan:
            speed_to_set = self.active_fan.get_status(0)['speed']
            self.gcode.run_script_from_command("SET_FAN_SPEED FAN='%s' SPEED=%s" % (self.active_fan.fan_name, 0.0))
        self.active_fan = fan
        if speed_to_set is not None:
            if self.active_fan:
                self.pending_speed = None
                self.gcode.run_script_from_command(
                    "SET_FAN_SPEED FAN='%s' SPEED=%s" % (self.active_fan.fan_name, speed_to_set))
            else:
                self.pending_speed = speed_to_set

    def cmd_M106(self, gcmd):
        tool = self.toolchanger.gcmd_tool(gcmd, default=self.toolchanger.active_tool, extra_number_arg='P')
        speed = gcmd.get_float('S', 255., minval=0.) / 255.
        self.set_speed(speed, tool)

    def cmd_M107(self, gcmd):
        tool = self.toolchanger.gcmd_tool(gcmd, default=self.toolchanger.active_tool, extra_number_arg='P')
        self.set_speed(0.0, tool)

    def set_speed(self, speed, tool):
        if tool and tool.fan:
            self.gcode.run_script_from_command("SET_FAN_SPEED FAN='%s' SPEED=%s" % (tool.fan.fan_name, speed))
        else:
            self.pending_speed = speed
>>>>>>> a85befe6eab3ab4da6a1de283d80b69f64b8dee7


def get_params_dict(config):
    result = {}
    for option in config.get_prefix_options('params_'):
        try:
            result[option] = ast.literal_eval(config.get(option))
        except ValueError:
            raise config.error(
                "Option '%s' in section '%s' is not a valid literal" %
                (option, config.get_name()))
    return result

def load_config(config):
    return Toolchanger(config)

def load_config_prefix(config):
    return Toolchanger(config)
