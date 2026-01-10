# Tool XY-Offset Calibration Module
# Saves XY offsets from kTAMV calibration to printer.cfg
#
# Commands:
#   SAVE_TOOL_XY_OFFSET TOOL=<n> X=<offset> Y=<offset> [INITIAL_TOOL=<n>]
#   SHOW_TOOL_XY_OFFSETS
#

class ToolXYCalibration:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')

        # Track calibrated offsets this session
        self.calibrated_offsets = {}

        # Register commands
        self.gcode.register_command(
            'SAVE_TOOL_XY_OFFSET',
            self.cmd_SAVE_TOOL_XY_OFFSET,
            desc="Save XY offset for a tool (prepares for SAVE_CONFIG)"
        )
        self.gcode.register_command(
            'SHOW_TOOL_XY_OFFSETS',
            self.cmd_SHOW_TOOL_XY_OFFSETS,
            desc="Display all calibrated XY offsets"
        )
        self.gcode.register_command(
            'KTAMV_AUTO_SAVE_OFFSET',
            self.cmd_KTAMV_AUTO_SAVE_OFFSET,
            desc="Auto-save XY offset from kTAMV last_calculated_offset"
        )

    def _get_toolchanger(self):
        """Get toolchanger object"""
        try:
            return self.printer.lookup_object('toolchanger')
        except:
            return None

    def cmd_SAVE_TOOL_XY_OFFSET(self, gcmd):
        """Save XY offset for a tool to printer.cfg"""
        tool_num = gcmd.get_int('TOOL')
        x_offset = gcmd.get_float('X')
        y_offset = gcmd.get_float('Y')

        # Determine initial tool (reference tool)
        toolchanger = self._get_toolchanger()
        if toolchanger and toolchanger.initial_tool:
            initial_tool_num = toolchanger.initial_tool.tool_number
        else:
            initial_tool_num = gcmd.get_int('INITIAL_TOOL', 0)

        # Store in session
        self.calibrated_offsets[tool_num] = (x_offset, y_offset)

        # Save to configfile in combined format: t{n}_xy_offset = X, Y
        # This matches the format that tool.py reads
        configfile = self.printer.lookup_object('configfile')
        tool_section = "tool T%d" % initial_tool_num

        # Combined format: "X, Y" (4 decimal places = 0.1µm precision)
        xy_offset_value = "%.4f, %.4f" % (x_offset, y_offset)
        configfile.set(tool_section, "t%d_xy_offset" % tool_num, xy_offset_value)

        gcmd.respond_info("T%d XY offset saved: %s" % (tool_num, xy_offset_value))
        gcmd.respond_info("Run SAVE_CONFIG to write to printer.cfg")

    def cmd_KTAMV_AUTO_SAVE_OFFSET(self, gcmd):
        """Auto-save XY offset from kTAMV's last_calculated_offset"""
        tool_num = gcmd.get_int('TOOL')

        # Try to get kTAMV object
        try:
            ktamv = self.printer.lookup_object('ktamv')
            if hasattr(ktamv, 'last_calculated_offset'):
                x_offset = ktamv.last_calculated_offset[0]
                y_offset = ktamv.last_calculated_offset[1]
            else:
                raise gcmd.error("kTAMV last_calculated_offset not available")
        except Exception as e:
            raise gcmd.error("Could not get kTAMV offset: %s" % str(e))

        # Determine initial tool
        toolchanger = self._get_toolchanger()
        if toolchanger and toolchanger.initial_tool:
            initial_tool_num = toolchanger.initial_tool.tool_number
        else:
            initial_tool_num = gcmd.get_int('INITIAL_TOOL', 0)

        # Store in session
        self.calibrated_offsets[tool_num] = (x_offset, y_offset)

        # Save to configfile in combined format: t{n}_xy_offset = X, Y
        configfile = self.printer.lookup_object('configfile')
        tool_section = "tool T%d" % initial_tool_num

        # Combined format: "X, Y" (4 decimal places = 0.1µm precision)
        xy_offset_value = "%.4f, %.4f" % (x_offset, y_offset)
        configfile.set(tool_section, "t%d_xy_offset" % tool_num, xy_offset_value)

        gcmd.respond_info("T%d XY offset auto-saved: %s" % (tool_num, xy_offset_value))

    def cmd_SHOW_TOOL_XY_OFFSETS(self, gcmd):
        """Display all calibrated XY offsets"""
        toolchanger = self._get_toolchanger()

        gcmd.respond_info("=" * 45)
        gcmd.respond_info("Tool XY-Offset Calibration Results")
        gcmd.respond_info("=" * 45)

        if not self.calibrated_offsets:
            gcmd.respond_info("No offsets calibrated this session")
        else:
            for tool_num in sorted(self.calibrated_offsets.keys()):
                x_off, y_off = self.calibrated_offsets[tool_num]
                gcmd.respond_info("  T%d: X=%.4f  Y=%.4f" % (tool_num, x_off, y_off))

        # Also show current offsets from toolchanger if available
        if toolchanger and toolchanger.initial_tool:
            initial_tool = toolchanger.initial_tool
            if hasattr(initial_tool, 'xy_offsets') and initial_tool.xy_offsets:
                gcmd.respond_info("")
                gcmd.respond_info("Currently loaded XY offsets (from config):")
                for tool_num, (x, y) in initial_tool.xy_offsets.items():
                    gcmd.respond_info("  T%d: X=%.4f  Y=%.4f" % (tool_num, x, y))

        gcmd.respond_info("=" * 45)


def load_config(config):
    return ToolXYCalibration(config)
