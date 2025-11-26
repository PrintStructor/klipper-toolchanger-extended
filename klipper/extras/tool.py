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
# - Stage-based gcode templates (pickup/dropoff stage1 + stage2)
# - Non-fatal error handling (prevents shutdown)
# - Tool detection state management
# - XY-offset matrix support (6 tools)
# - Recovery system with RECOVER_TOOL command
# - Convenience properties for stage access
# - Defensive object resolution
#
# This file may be distributed under the terms of the GNU GPLv3 license.

from . import toolchanger

# ==============================================================================
#                              Tool Class
# ==============================================================================

class Tool:

    def __init__(self, config):
        # ==============================================================================
        #                          Initialization
        # ==============================================================================
        self.printer = config.get_printer()
        self.config = config
        self.gcode = self.printer.lookup_object('gcode')
        self.params = config.get_prefix_options('params_')
        self.gcode_macro = self.printer.load_object(config, 'gcode_macro')
        self.name = config.get_name()
        toolchanger_name = config.get('toolchanger', 'toolchanger')
        self.main_toolchanger = self.printer.load_object(config, 'toolchanger')
        self.toolchanger = self.printer.load_object(config, toolchanger_name)

        self.pickup_gcode = self.gcode_macro.load_template(
            config, 'pickup_gcode', self._config_get(config, 'pickup_gcode', ''))
        self.dropoff_gcode = self.gcode_macro.load_template(
            config, 'dropoff_gcode', self._config_get(config, 'dropoff_gcode', ''))
        self.before_change_gcode = self.gcode_macro.load_template(
            config, 'before_change_gcode', self._config_get(config, 'before_change_gcode', ''))
        self.after_change_gcode = self.gcode_macro.load_template(
            config, 'after_change_gcode', self._config_get(config, 'after_change_gcode', ''))
        
        # Recovery G-code for error handling
        self.recover_gcode = self.gcode_macro.load_template(
            config, 'recover_gcode', self._config_get(config, 'recover_gcode', ''))
        
        # Split pickup/dropoff into two stages
        self.pickup_gcode_stage1 = self.gcode_macro.load_template(
            config, 'pickup_gcode_stage1', self._config_get(config, 'pickup_gcode_stage1', ''))
        self.pickup_gcode_stage2 = self.gcode_macro.load_template(
            config, 'pickup_gcode_stage2', self._config_get(config, 'pickup_gcode_stage2', ''))
        self.dropoff_gcode_stage1 = self.gcode_macro.load_template(
            config, 'dropoff_gcode_stage1', self._config_get(config, 'dropoff_gcode_stage1', ''))
        self.dropoff_gcode_stage2 = self.gcode_macro.load_template(
            config, 'dropoff_gcode_stage2', self._config_get(config, 'dropoff_gcode_stage2', ''))

        self.gcode_x_offset = self._config_getfloat(config, 'gcode_x_offset', 0.0)
        self.gcode_y_offset = self._config_getfloat(config, 'gcode_y_offset', 0.0)
        self.gcode_z_offset = self._config_getfloat(config, 'gcode_z_offset', 0.0)

        self.params = {**self.toolchanger.params, **toolchanger.get_params_dict(config)}
        self.original_params = {}

        self.extruder_name = self._config_get(config, 'extruder', None)
        detect_pin_name = config.get('detection_pin', None)
        self.detect_state = toolchanger.DETECT_UNAVAILABLE
        if detect_pin_name:
            self.printer.load_object(config, 'buttons').register_buttons([detect_pin_name], self._handle_detect)
            self.detect_state = toolchanger.DETECT_ABSENT

        self.extruder_stepper_name = self._config_get(config, 'extruder_stepper', None)
        self.extruder = None
        self.extruder_stepper = None
        self.fan_name = self._config_get(config, 'fan', None)
        self.fan = None
        self.t_command_restore_axis = self._config_get(config, 't_command_restore_axis', 'XYZ')
        self.tool_number = config.getint('tool_number', -1, minval=0)

        # Z-offset matrix (dynamically sized based on toolchanger config)
        max_tool_count = self.toolchanger.params.get('max_tool_count', 6)
        self.z_offsets = {}
        for i in range(max_tool_count):
            if i != self.tool_number:
                offset_name = f't{i}_z_offset'
                offset = config.getfloat(offset_name, None)
                if offset is not None:
                    self.z_offsets[i] = offset

        # X-Y offset matrix (dynamically sized based on toolchanger config)
        self.xy_offsets = {}
        for i in range(max_tool_count):
            if i != self.tool_number:
                offset_name = f't{i}_xy_offset'
                offset = config.get(offset_name, None)
                if offset is not None:
                    try:
                        x_offset, y_offset = map(float, offset.split(','))
                        self.xy_offsets[i] = [x_offset, y_offset]
                    except ValueError:
                        pass

        gcode = self.printer.lookup_object('gcode')
        gcode.register_mux_command("ASSIGN_TOOL", "TOOL", self.name,
                                   self.cmd_ASSIGN_TOOL,
                                   desc=self.cmd_ASSIGN_TOOL_help)
        gcode.register_mux_command("RECOVER_TOOL", "TOOL", self.name,
                                   self.cmd_RECOVER_TOOL,
                                   desc=self.cmd_RECOVER_TOOL_help)

        self.printer.register_event_handler("klippy:connect", self._handle_connect)

        # Non-fatal command error policy
        self._pause_on_error = True

    # ==============================================================================
    #                       Non-fatal Error Utilities
    # ==============================================================================
    
    def _report_nonfatal(self, gcmd, msg):
        """Visible error without raising (prevents shutdown)."""
        try:
            if gcmd is not None:
                gcmd.respond_error(msg)
            else:
                self.gcode.respond_error(msg)
        except Exception:
            pass

    def _pause_print(self):
        """Pause the print safely (optional)."""
        if not self._pause_on_error:
            return
        try:
            self.printer.lookup_object('pause_resume').send_pause()
        except Exception:
            try:
                self.gcode.run_script_from_command("PAUSE")
            except Exception:
                pass

    # ==============================================================================
    #                          Event Handlers
    # ==============================================================================
    
    def _handle_connect(self):
        # Resolve optional objects defensively
        try:
            self.extruder = self.printer.lookup_object(self.extruder_name) if self.extruder_name else None
        except Exception:
            self.extruder = None
        try:
            self.extruder_stepper = self.printer.lookup_object(self.extruder_stepper_name) if self.extruder_stepper_name else None
        except Exception:
            self.extruder_stepper = None
        try:
            self.fan = self.printer.lookup_object(self.fan_name) if self.fan_name else None
        except Exception:
            self.fan = None

        # Assign tool number (may raise at config-time; here we guard and just log)
        if self.tool_number >= 0:
            try:
                self.assign_tool(self.tool_number)
            except Exception as e:
                self.gcode.respond_info(f"Tool {_safe(self.name)} failed to assign on connect: {e}")

    def _handle_detect(self, eventtime, is_triggered):
        # Mapping for your setup:
        # Pin HIGH (True)  = Tool detected (on shuttle)  -> DETECT_PRESENT
        # Pin LOW  (False) = Tool not detected (in dock) -> DETECT_ABSENT
        old_state = self.detect_state
        self.detect_state = toolchanger.DETECT_PRESENT if is_triggered else toolchanger.DETECT_ABSENT

        try:
            self.toolchanger.note_detect_change(self)

            # Check for tool loss during active print
            # CRITICAL: Only trigger if a print is actually running or paused!
            # Prevents false alarms when manually changing tools after:
            # - Print completion, CANCEL_PRINT, or manual tool changes
            virtual_sdcard = self.printer.lookup_object('virtual_sdcard', None)
            pause_resume = self.printer.lookup_object('pause_resume', None)
            is_printing = (virtual_sdcard and virtual_sdcard.is_active()) or \
                          (pause_resume and pause_resume.is_paused)

            if (self == self.toolchanger.active_tool and
                self.toolchanger.status == toolchanger.STATUS_READY and
                old_state == toolchanger.DETECT_PRESENT and
                self.detect_state != toolchanger.DETECT_PRESENT and
                is_printing):  # ← Only trigger during active print or pause!
                # Tool has dropped during print! Call safety handler
                self._handle_tool_loss()
        except Exception as e:
            self.gcode.respond_info(f"Tool detect state update failed: {e}")

    def _handle_tool_loss(self):
        """Called when active tool is lost during operation (event-driven)."""
        # 1. PAUSE print IMMEDIATELY (fastest response - before macro execution)
        #    This stops the print and saves position automatically
        self.gcode.run_script_from_command("PAUSE")

        try:
            # 2. Call the configured safety macro (heater off, Z-lift if safe, LED)
            self.gcode.run_script_from_command("_TOOLCHANGER_TOOL_LOSS_HANDLER T=%d" % self.tool_number)
        except Exception as e:
            # Fallback: at minimum, report the error
            self.gcode.respond_info(f"🚨 CRITICAL: Tool T{self.tool_number} lost! Handler failed: {e}")
            # Try to pause as last resort
            try:
                self.printer.lookup_object('pause_resume').send_pause()
            except Exception:
                pass

    # ==============================================================================
    #                        Status & Offsets
    # ==============================================================================
    
    def get_status(self, eventtime):
        active = False
        try:
            sel = self.main_toolchanger.get_selected_tool()
            active = (sel is not None and sel.tool_number == self.tool_number)
        except Exception:
            active = False
        return {
            **self.params,
            'name': self.name,
            'toolchanger': self.toolchanger.name,
            'tool_number': self.tool_number,
            'extruder': self.extruder_name,
            'extruder_stepper': self.extruder_stepper_name,
            'fan': self.fan_name,
            'active': active,
            'gcode_x_offset': self.gcode_x_offset if self.gcode_x_offset else 0.0,
            'gcode_y_offset': self.gcode_y_offset if self.gcode_y_offset else 0.0,
            'gcode_z_offset': self.gcode_z_offset if self.gcode_z_offset else 0.0,
            'z_offsets': self.z_offsets,
            'xy_offsets': self.xy_offsets,
            'detect_state': self.detect_state,
        }

    def get_offset(self):
        return [
            self.gcode_x_offset if self.gcode_x_offset else 0.0,
            self.gcode_y_offset if self.gcode_y_offset else 0.0,
            self.gcode_z_offset if self.gcode_z_offset else 0.0,
        ]

    def get_z_offset_to_tool(self, tool_number):
        """Return the Z offset to another tool."""
        return self.z_offsets.get(tool_number, 0.0)

    def get_xy_offset_to_tool(self, tool_number):
        """Return the stored X-Y offset to another tool."""
        return self.xy_offsets.get(tool_number, [0.0, 0.0])

    # ==============================================================================
    #                    Convenience Properties (Stage Access)
    # ==============================================================================
    
    @property
    def before_change(self):
        return self.before_change_gcode

    @property
    def after_change(self):
        return self.after_change_gcode

    @property
    def pickup_stage1(self):
        return self.pickup_gcode_stage1 if self.pickup_gcode_stage1 is not None else self.pickup_gcode

    @property
    def pickup_stage2(self):
        return self.pickup_gcode_stage2

    @property
    def dropoff_stage1(self):
        return self.dropoff_gcode_stage1 if self.dropoff_gcode_stage1 is not None else self.dropoff_gcode

    @property
    def dropoff_stage2(self):
        return self.dropoff_gcode_stage2

    # ==============================================================================
    #                          Recovery System
    # ==============================================================================
    
    def recover(self, gcmd):
        """Recovery procedure for this tool after an error."""
        if not self.recover_gcode:
            try:
                gcmd.respond_info(f"No recovery gcode defined for {self.name}")
            except Exception:
                pass
            return

        try:
            gcmd.respond_info(f"Starting recovery for {self.name}...")
        except Exception:
            pass

        extra_context = {
            'tool': self.name,
            'tool_number': self.tool_number,
        }

        try:
            self.toolchanger.run_gcode('tool.recover_gcode', self.recover_gcode, extra_context)
            try:
                gcmd.respond_info(f"Recovery completed for {self.name}")
            except Exception:
                pass
        except Exception as e:
            self._report_nonfatal(gcmd, f"Recovery failed for {self.name}: {e}")
            self._pause_print()
            return

    cmd_RECOVER_TOOL_help = 'Attempt to recover this tool from error state'
    
    def cmd_RECOVER_TOOL(self, gcmd):
        self.recover(gcmd)

    # ==============================================================================
    #                      Assignment & Registration
    # ==============================================================================
    
    cmd_ASSIGN_TOOL_help = 'Assign tool to tool number'
    
    def cmd_ASSIGN_TOOL(self, gcmd):
        try:
            number = gcmd.get_int('N', minval=0)
        except Exception as e:
            self._report_nonfatal(gcmd, f"ASSIGN_TOOL: invalid or missing N: {e}")
            self._pause_print()
            return

        try:
            self.assign_tool(number, replace=True)
            try:
                gcmd.respond_info(f"Tool {self.name} assigned to T{number}")
            except Exception:
                pass
        except Exception as e:
            self._report_nonfatal(gcmd, f"ASSIGN_TOOL failed for {self.name}: {e}")
            self._pause_print()
            return

    def assign_tool(self, number, replace=False):
        prev_number = self.tool_number
        self.tool_number = number
        self.main_toolchanger.assign_tool(self, number, prev_number, replace)
        self.register_t_gcode(number)

    def register_t_gcode(self, number):
        gcode = self.printer.lookup_object('gcode')
        name = 'T%d' % (number)
        desc = 'Select tool %d' % (number)
        existing = gcode.register_command(name, None)
        if existing:
            gcode.register_command(name, existing)
        else:
            tc = self.main_toolchanger
            axis = self.t_command_restore_axis
            def _select(gcmd):
                try:
                    tc.select_tool(gcmd, tc.lookup_tool(number), axis)
                except Exception as e:
                    try:
                        gcmd.respond_error(f"T{number} selection failed: {e}")
                    except Exception:
                        pass
                    try:
                        self.printer.lookup_object('pause_resume').send_pause()
                    except Exception:
                        try:
                            gcode.run_script_from_command("PAUSE")
                        except Exception:
                            pass
                    return
            gcode.register_command(name, _select, desc=desc)

    # ==============================================================================
    #                      Activation / Deactivation
    # ==============================================================================
    
    def activate(self):
        toolhead = self.printer.lookup_object('toolhead')
        gcode = self.printer.lookup_object('gcode')
        hotend_extruder = toolhead.get_extruder().name
        if self.extruder_name and self.extruder_name != hotend_extruder:
            gcode.run_script_from_command("ACTIVATE_EXTRUDER EXTRUDER='%s'" % (self.extruder_name,))
        if self.extruder_stepper and hotend_extruder:
            gcode.run_script_from_command(
                "SYNC_EXTRUDER_MOTION EXTRUDER='%s' MOTION_QUEUE=" % (hotend_extruder, ))
            gcode.run_script_from_command(
                "SYNC_EXTRUDER_MOTION EXTRUDER='%s' MOTION_QUEUE='%s'" %
                (self.extruder_stepper_name, hotend_extruder, ))
        if self.fan:
            gcode.run_script_from_command("ACTIVATE_FAN FAN='%s'" % (self.fan.name,))

    def deactivate(self):
        if self.extruder_stepper:
            toolhead = self.printer.lookup_object('toolhead')
            gcode = self.printer.lookup_object('gcode')
            hotend_extruder = toolhead.get_extruder().name
            gcode.run_script_from_command(
                "SYNC_EXTRUDER_MOTION EXTRUDER='%s' MOTION_QUEUE=" % (self.extruder_stepper_name,))
            gcode.run_script_from_command(
                "SYNC_EXTRUDER_MOTION EXTRUDER='%s' MOTION_QUEUE=%s" %
                (hotend_extruder, hotend_extruder,))

    # ==============================================================================
    #                          Config Helpers
    # ==============================================================================
    
    def _config_get(self, config, name, default_value):
        return config.get(name, self.toolchanger.config.get(name, default_value))
    
    def _config_getfloat(self, config, name, default_value):
        return config.getfloat(name, self.toolchanger.config.getfloat(name, default_value))
    
    def _config_getboolean(self, config, name, default_value):
        return config.getboolean(name, self.toolchanger.config.getboolean(name, default_value))

# ==============================================================================
#                          Module Hooks
# ==============================================================================

def load_config(config):
    return Tool(config)

def load_config_prefix(config):
    return Tool(config)

# ==============================================================================
#                          Utility Functions
# ==============================================================================

def _safe(x):
    try:
        return str(x)
    except Exception:
        return "<unknown>"
