# Tool Z-Offset Adjustment Module
# Allows per-tool Z-offset fine-tuning during printing
#
# This module directly modifies the toolchanger's z_offsets dictionary,
# which is automatically applied during tool changes.
#
# Features:
# - Adjustments are made in RAM (no SD card writes during print)
# - Toolchanger applies offsets automatically on tool change
# - Optional save to printer.cfg via SAVE_CONFIG
# - Reset to calibrated values without full recalibration
# - ALL tools treated equally (including initial/reference tool)
#
# Commands:
#   SET_TOOL_Z_ADJUST [TOOL=<n>] [Z=<offset>] [RESET=1]
#   SHOW_TOOL_Z_ADJUSTMENTS
#   SAVE_TOOL_Z_ADJUSTMENTS
#   CHECK_TOOL_Z_ADJUSTMENTS (for PRINT_END integration)

class ToolZAdjust:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')

        # Store original offsets (loaded from config) for reset functionality
        self.original_offsets = {}
        # Track adjustments made this session (for display purposes)
        self.session_adjustments = {}

        # Register commands
        self.gcode.register_command(
            'SET_TOOL_Z_ADJUST',
            self.cmd_SET_TOOL_Z_ADJUST,
            desc="Adjust Z-offset for a tool (RAM only until saved)"
        )
        self.gcode.register_command(
            'SHOW_TOOL_Z_ADJUSTMENTS',
            self.cmd_SHOW_TOOL_Z_ADJUSTMENTS,
            desc="Display all tool Z-offset adjustments"
        )
        self.gcode.register_command(
            'SAVE_TOOL_Z_ADJUSTMENTS',
            self.cmd_SAVE_TOOL_Z_ADJUSTMENTS,
            desc="Save Z-adjustments permanently via SAVE_CONFIG"
        )
        self.gcode.register_command(
            'CHECK_TOOL_Z_ADJUSTMENTS',
            self.cmd_CHECK_TOOL_Z_ADJUSTMENTS,
            desc="Check if there are unsaved adjustments (for PRINT_END)"
        )

        # Register event handler to capture original offsets after config loaded
        self.printer.register_event_handler("klippy:ready", self._handle_ready)

    def _handle_ready(self):
        """Capture original z_offsets after toolchanger is fully initialized"""
        try:
            toolchanger = self.printer.lookup_object('toolchanger')
            if toolchanger.initial_tool and hasattr(toolchanger.initial_tool, 'z_offsets'):
                initial_tool = toolchanger.initial_tool

                # Initialize initial tool's own z_offset to 0 if not present
                # This allows the initial tool to be adjusted like any other tool
                if initial_tool.tool_number not in initial_tool.z_offsets:
                    initial_tool.z_offsets[initial_tool.tool_number] = 0.0

                # Deep copy all original offsets (including initial tool)
                self.original_offsets = dict(initial_tool.z_offsets)

                # Ensure initial tool has an original offset entry
                if initial_tool.tool_number not in self.original_offsets:
                    self.original_offsets[initial_tool.tool_number] = 0.0

        except Exception as e:
            self.gcode.respond_info("Tool Z-Adjust: Could not capture original offsets: %s" % str(e))

    def _get_toolchanger(self):
        """Get toolchanger object"""
        try:
            return self.printer.lookup_object('toolchanger')
        except:
            return None

    def _get_initial_tool(self):
        """Get initial tool object that holds z_offsets"""
        toolchanger = self._get_toolchanger()
        if toolchanger and toolchanger.initial_tool:
            return toolchanger.initial_tool
        return None

    def _apply_offset_to_current_tool(self, tool_number, new_offset):
        """If the adjusted tool is currently active, update gcode offset immediately"""
        toolchanger = self._get_toolchanger()
        if not toolchanger or not toolchanger.active_tool:
            return

        if toolchanger.active_tool.tool_number == tool_number:
            # Recalculate and apply the offset
            try:
                globals_macro = self.printer.lookup_object('gcode_macro globals')
                global_offset = globals_macro.variables.get('global_z_offset', 0.0)
            except:
                global_offset = 0.0

            total_offset = new_offset + global_offset
            # Use _BASE_SET_GCODE_OFFSET to avoid recursive macro call
            self.gcode.run_script_from_command('_BASE_SET_GCODE_OFFSET Z=%.4f MOVE=1' % total_offset)

    def cmd_SET_TOOL_Z_ADJUST(self, gcmd):
        """Adjust Z-offset for a tool (all tools treated equally)"""
        toolchanger = self._get_toolchanger()
        if not toolchanger:
            raise gcmd.error("Toolchanger not found")

        initial_tool = self._get_initial_tool()
        if not initial_tool or not hasattr(initial_tool, 'z_offsets'):
            raise gcmd.error("Initial tool or z_offsets not available")

        # Determine which tool to adjust
        tool_num = gcmd.get_int('TOOL', None)
        if tool_num is None:
            if toolchanger.active_tool:
                tool_num = toolchanger.active_tool.tool_number
            else:
                raise gcmd.error("No tool specified and no active tool")

        reset = gcmd.get_int('RESET', 0)
        z_adjust = gcmd.get_float('Z', None)

        # Get current and original offsets (works for ALL tools including initial)
        current_offset = initial_tool.z_offsets.get(tool_num, 0.0)
        original_offset = self.original_offsets.get(tool_num, 0.0)

        if reset:
            # Reset to original calibrated value
            new_offset = original_offset
            initial_tool.z_offsets[tool_num] = new_offset

            # Remove from session adjustments
            if tool_num in self.session_adjustments:
                del self.session_adjustments[tool_num]

            gcmd.respond_info("T%d Z-offset reset to calibrated value: %.4f mm" %
                            (tool_num, new_offset))
        elif z_adjust is not None:
            # Add adjustment to current offset
            new_offset = current_offset + z_adjust
            initial_tool.z_offsets[tool_num] = new_offset

            # Track the adjustment
            self.session_adjustments[tool_num] = new_offset - original_offset

            delta_um = z_adjust * 1000
            gcmd.respond_info("T%d Z-offset: %.4f -> %.4f mm (%s%.1f um)" %
                            (tool_num, current_offset, new_offset,
                             '+' if z_adjust > 0 else '', delta_um))
        else:
            # Just show current value
            adjustment = current_offset - original_offset
            adj_um = adjustment * 1000
            gcmd.respond_info("T%d Z-offset: %.4f mm (calibrated: %.4f, adjustment: %s%.1f um)" %
                            (tool_num, current_offset, original_offset,
                             '+' if adjustment >= 0 else '', adj_um))
            return

        # Apply immediately if this is the active tool
        self._apply_offset_to_current_tool(tool_num, new_offset)

    def cmd_SHOW_TOOL_Z_ADJUSTMENTS(self, gcmd):
        """Display all tool Z-offset adjustments"""
        initial_tool = self._get_initial_tool()
        toolchanger = self._get_toolchanger()

        if not initial_tool:
            raise gcmd.error("Initial tool not available")

        active_tool_num = -1
        if toolchanger and toolchanger.active_tool:
            active_tool_num = toolchanger.active_tool.tool_number

        gcmd.respond_info("=" * 45)
        gcmd.respond_info("Tool Z-Offset Adjustments")
        gcmd.respond_info("Initial Tool: T%d" % initial_tool.tool_number)
        gcmd.respond_info("=" * 45)

        has_adjustments = False
        # Get all known tool numbers from z_offsets and original_offsets
        all_tools = set(initial_tool.z_offsets.keys()) | set(self.original_offsets.keys())
        for i in sorted(all_tools):
            current = initial_tool.z_offsets.get(i, 0.0)
            original = self.original_offsets.get(i, 0.0)
            adjustment = current - original

            marker = " <-- ACTIVE" if i == active_tool_num else ""
            ref_marker = " [INIT]" if i == initial_tool.tool_number else ""

            if abs(adjustment) > 0.0001:
                has_adjustments = True
                adj_um = adjustment * 1000
                gcmd.respond_info("  T%d: %.4f mm (adj: %s%.1f um)%s%s" %
                                (i, current, '+' if adjustment >= 0 else '', adj_um, ref_marker, marker))
            else:
                gcmd.respond_info("  T%d: %.4f mm%s%s" % (i, current, ref_marker, marker))

        gcmd.respond_info("=" * 45)
        if has_adjustments:
            gcmd.respond_info("* Unsaved adjustments - use SAVE_TOOL_Z_ADJUSTMENTS to keep")
        else:
            gcmd.respond_info("No adjustments made this session")

    def cmd_SAVE_TOOL_Z_ADJUSTMENTS(self, gcmd):
        """Save Z-adjustments permanently via SAVE_CONFIG"""
        initial_tool = self._get_initial_tool()
        if not initial_tool:
            raise gcmd.error("Initial tool not available")

        if not self.session_adjustments:
            gcmd.respond_info("No adjustments to save")
            return

        configfile = self.printer.lookup_object('configfile')
        tool_section = "tool T%d" % initial_tool.tool_number

        saved_tools = []
        for tool_num, adjustment in self.session_adjustments.items():
            new_offset = initial_tool.z_offsets.get(tool_num, 0.0)
            option_name = "t%d_z_offset" % tool_num
            configfile.set(tool_section, option_name, "%.4f" % new_offset)
            saved_tools.append("T%d" % tool_num)

            # Update original offsets so future resets use new values
            self.original_offsets[tool_num] = new_offset

        # Clear session adjustments
        self.session_adjustments.clear()

        gcmd.respond_info("Z-adjustments prepared for save: %s" % ", ".join(saved_tools))
        gcmd.respond_info("Run SAVE_CONFIG to write changes to printer.cfg")
        gcmd.respond_info("NOTE: SAVE_CONFIG will restart Klipper!")

    def cmd_CHECK_TOOL_Z_ADJUSTMENTS(self, gcmd):
        """Check if there are unsaved adjustments - for PRINT_END integration"""
        if not self.session_adjustments:
            gcmd.respond_info("TOOL_Z_ADJUSTMENTS_STATUS: NONE")
            return

        initial_tool = self._get_initial_tool()
        if not initial_tool:
            gcmd.respond_info("TOOL_Z_ADJUSTMENTS_STATUS: NONE")
            return

        # Build summary of adjustments
        changes = []
        for tool_num, adjustment in self.session_adjustments.items():
            original = self.original_offsets.get(tool_num, 0.0)
            new_offset = initial_tool.z_offsets.get(tool_num, 0.0)
            adj_um = adjustment * 1000
            changes.append("T%d: %.4f -> %.4f (%s%.1f um)" %
                          (tool_num, original, new_offset,
                           '+' if adjustment >= 0 else '', adj_um))

        gcmd.respond_info("TOOL_Z_ADJUSTMENTS_STATUS: UNSAVED")
        gcmd.respond_info("Unsaved Z-offset adjustments:")
        for change in changes:
            gcmd.respond_info("  %s" % change)
        gcmd.respond_info("Use SAVE_TOOL_Z_ADJUSTMENTS then SAVE_CONFIG to keep these changes")


def load_config(config):
    return ToolZAdjust(config)
