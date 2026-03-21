# TMC4671 Crash Detection Module for Klipper
# ==============================================================================
#
# Author: PrintStructor
# Version: 0.1.0-alpha (EXPERIMENTAL)
# License: GPL-3.0
#
# Description:
#   Monitors TMC4671 position tracking error via SPI register reads.
#   When the difference between commanded and actual position exceeds
#   a configurable threshold, triggers a print pause to prevent damage.
#
#   This leverages the TMC4671's closed-loop servo control — the chip
#   always knows the real motor position via encoder feedback. If the
#   motor can't reach the commanded position (crash, blockage, belt skip),
#   the position error grows. We detect that and react.
#
# TMC4671 Registers Used:
#   PID_POSITION_TARGET (0x68) - Where the motor should be
#   PID_POSITION_ACTUAL  (0x6B) - Where the motor actually is
#   PID_ERROR_ADDR       (0x6D) - Select which PID error to read
#   PID_ERROR_DATA       (read via INTERIM) - The error value
#   STATUS_FLAGS         (0x7C) - Hardware status flags
#
# Prerequisites:
#   - Andrew McGrath's TMC4671 Klipper driver installed
#   - TMC4671 configured and working in closed-loop mode
#   - Encoder feedback operational
#
# Configuration Example:
#   [tmc4671_crash_detect]
#   stepper_x: stepper_x          # Which stepper to monitor
#   stepper_y: stepper_y          # Can monitor multiple axes
#   position_error_threshold: 200  # Error threshold (encoder counts)
#   check_interval: 0.1            # How often to check (seconds)
#   consecutive_errors: 3          # How many consecutive over-threshold reads
#   enabled_during_print: True     # Only active during printing
#   pause_on_error: True           # Pause print when crash detected
#
# GCode Commands:
#   TMC4671_CRASH_DETECT_ENABLE    - Enable monitoring
#   TMC4671_CRASH_DETECT_DISABLE   - Disable monitoring
#   TMC4671_CRASH_DETECT_STATUS    - Show current position errors
#   TMC4671_CRASH_DETECT_TEST      - Test detection (simulated error)
#
# ==============================================================================

import logging

# TMC4671 Register Addresses
TMC4671_PID_POSITION_TARGET = 0x68
TMC4671_PID_POSITION_ACTUAL = 0x6B
TMC4671_PID_ERROR_ADDR = 0x6D
TMC4671_INTERIM_DATA = 0x6E
TMC4671_INTERIM_ADDR = 0x6F
TMC4671_STATUS_FLAGS = 0x7C
TMC4671_STATUS_MASK = 0x7D

# PID Error Address selections (write to PID_ERROR_ADDR to select)
PID_POSITION_ERROR = 2
PID_VELOCITY_ERROR = 1
PID_TORQUE_ERROR = 0

class TMC4671CrashDetect:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()
        self.gcode = self.printer.lookup_object('gcode')
        self.name = config.get_name()

        # Configuration
        self.stepper_names = []
        for option in ['stepper_x', 'stepper_y']:
            name = config.get(option, None)
            if name is not None:
                self.stepper_names.append(name)

        self.error_threshold = config.getint(
            'position_error_threshold', 200)
        self.check_interval = config.getfloat(
            'check_interval', 0.1)
        self.consecutive_required = config.getint(
            'consecutive_errors', 3)
        self.enabled_during_print = config.getboolean(
            'enabled_during_print', True)
        self.pause_on_error = config.getboolean(
            'pause_on_error', True)

        # State
        self.is_monitoring = False
        self.tmc_objects = {}
        self.error_counters = {}
        self.last_errors = {}
        self.timer_handle = None

        # Register event handlers
        self.printer.register_event_handler(
            "klippy:ready", self._handle_ready)
        self.printer.register_event_handler(
            "print_stats:printing", self._handle_printing)
        self.printer.register_event_handler(
            "print_stats:paused", self._handle_paused)
        self.printer.register_event_handler(
            "print_stats:complete", self._handle_complete)
        self.printer.register_event_handler(
            "print_stats:cancelled", self._handle_complete)

        # Register GCode commands
        self.gcode.register_command(
            'TMC4671_CRASH_DETECT_ENABLE',
            self.cmd_ENABLE,
            desc="Enable TMC4671 crash detection monitoring")
        self.gcode.register_command(
            'TMC4671_CRASH_DETECT_DISABLE',
            self.cmd_DISABLE,
            desc="Disable TMC4671 crash detection monitoring")
        self.gcode.register_command(
            'TMC4671_CRASH_DETECT_STATUS',
            self.cmd_STATUS,
            desc="Show current TMC4671 position tracking errors")

    def _handle_ready(self):
        """Lookup TMC4671 driver objects once Klipper is ready."""
        for stepper_name in self.stepper_names:
            # Try to find the tmc4671 config section for this stepper
            tmc_name = "tmc4671 %s" % stepper_name
            try:
                tmc = self.printer.lookup_object(tmc_name)
                self.tmc_objects[stepper_name] = tmc
                self.error_counters[stepper_name] = 0
                self.last_errors[stepper_name] = 0
                logging.info(
                    "tmc4671_crash_detect: Found %s" % tmc_name)
            except Exception as e:
                logging.warning(
                    "tmc4671_crash_detect: Could not find %s: %s"
                    % (tmc_name, str(e)))
        if not self.tmc_objects:
            logging.error(
                "tmc4671_crash_detect: No TMC4671 drivers found!")

    def _handle_printing(self, *args):
        """Auto-start monitoring when print begins."""
        if self.enabled_during_print and self.tmc_objects:
            self._start_monitoring()

    def _handle_paused(self, *args):
        """Stop monitoring during pause (avoid false triggers)."""
        self._stop_monitoring()

    def _handle_complete(self, *args):
        """Stop monitoring when print ends."""
        self._stop_monitoring()

    def _start_monitoring(self):
        """Begin periodic position error checking."""
        if self.is_monitoring:
            return
        self.is_monitoring = True
        for name in self.error_counters:
            self.error_counters[name] = 0
        self.timer_handle = self.reactor.register_timer(
            self._check_position_error,
            self.reactor.monotonic() + self.check_interval)
        self.gcode.respond_info(
            "TMC4671 crash detection: ACTIVE (threshold=%d, interval=%.1fs)"
            % (self.error_threshold, self.check_interval))

    def _stop_monitoring(self):
        """Stop periodic checking."""
        if not self.is_monitoring:
            return
        self.is_monitoring = False
        if self.timer_handle is not None:
            self.reactor.unregister_timer(self.timer_handle)
            self.timer_handle = None

    def _read_register(self, tmc_obj, reg_addr):
        """Read a TMC4671 register via SPI.

        NOTE: This method may need adjustment depending on
        Andrew's tmc4671.py driver API. The TMC4671 driver
        should expose SPI read access. Common patterns:
          - tmc_obj.mcu_tmc.get_register(reg_addr)
          - tmc_obj.spi.spi_transfer([reg_addr, 0,0,0,0])
        If the driver API differs, adjust this method.
        The SPI protocol for TMC4671 is:
          TX: [addr(7bit) + R/W(1bit)] [data_31:24] [data_23:16] [data_15:8] [data_7:0]
          For read: addr byte MSB = 0 (read mode)
        """
        try:
            # Attempt 1: Direct register read via driver API
            if hasattr(tmc_obj, 'get_register'):
                return tmc_obj.get_register(reg_addr)
            # Attempt 2: Via mcu_tmc object
            if hasattr(tmc_obj, 'mcu_tmc'):
                if hasattr(tmc_obj.mcu_tmc, 'get_register'):
                    return tmc_obj.mcu_tmc.get_register(reg_addr)
            # Attempt 3: Direct SPI transfer
            if hasattr(tmc_obj, 'spi'):
                # TMC4671 SPI read: send addr with MSB=0, receive 4 data bytes
                params = tmc_obj.spi.spi_transfer(
                    [reg_addr & 0x7F, 0x00, 0x00, 0x00, 0x00])
                response = bytearray(params['response'])
                # First byte is status, bytes 1-4 are register data
                val = ((response[1] << 24) | (response[2] << 16) |
                       (response[3] << 8) | response[4])
                # Handle signed 32-bit
                if val >= 0x80000000:
                    val -= 0x100000000
                return val
            logging.warning(
                "tmc4671_crash_detect: Cannot read register - "
                "unknown driver API")
            return None
        except Exception as e:
            logging.debug(
                "tmc4671_crash_detect: SPI read error: %s" % str(e))
            return None

    def _get_position_error(self, stepper_name):
        """Read position error for a stepper axis.

        Computes: abs(PID_POSITION_TARGET - PID_POSITION_ACTUAL)
        This is the core metric: how far is the motor from where
        it should be? During normal operation this is near zero.
        During a crash/stall, this grows rapidly.
        """
        tmc = self.tmc_objects.get(stepper_name)
        if tmc is None:
            return None

        target = self._read_register(tmc, TMC4671_PID_POSITION_TARGET)
        actual = self._read_register(tmc, TMC4671_PID_POSITION_ACTUAL)

        if target is None or actual is None:
            return None

        return abs(target - actual)

    def _check_position_error(self, eventtime):
        """Periodic callback: check position errors on all monitored axes."""
        if not self.is_monitoring:
            return self.reactor.NEVER

        crash_detected = False
        crash_axis = None

        for stepper_name in self.tmc_objects:
            error = self._get_position_error(stepper_name)
            if error is None:
                continue

            self.last_errors[stepper_name] = error

            if error > self.error_threshold:
                self.error_counters[stepper_name] += 1
                if self.error_counters[stepper_name] >= self.consecutive_required:
                    crash_detected = True
                    crash_axis = stepper_name
                    break
            else:
                # Reset counter when error is within threshold
                self.error_counters[stepper_name] = 0

        if crash_detected:
            self._handle_crash(crash_axis)
            return self.reactor.NEVER

        # Schedule next check
        return eventtime + self.check_interval

    def _handle_crash(self, axis_name):
        """Handle a detected crash event."""
        self.is_monitoring = False
        error_val = self.last_errors.get(axis_name, 0)

        logging.error(
            "tmc4671_crash_detect: CRASH DETECTED on %s! "
            "Position error: %d (threshold: %d)"
            % (axis_name, error_val, self.error_threshold))

        # Report to user
        self.gcode.respond_raw(
            "!! TMC4671 CRASH DETECTED on %s "
            "(position error: %d counts)" % (axis_name, error_val))

        if self.pause_on_error:
            # Trigger pause via the same mechanism as tool-loss detection
            try:
                self.gcode.run_script_from_command("PAUSE")
                self.gcode.respond_info(
                    "Print paused due to crash detection on %s. "
                    "Check for obstructions, then RESUME."
                    % axis_name)
            except Exception as e:
                logging.error(
                    "tmc4671_crash_detect: Failed to pause: %s"
                    % str(e))

    # ==================================================================
    # GCode Command Handlers
    # ==================================================================

    def cmd_ENABLE(self, gcmd):
        """Enable crash detection monitoring."""
        if not self.tmc_objects:
            gcmd.respond_info("ERROR: No TMC4671 drivers configured")
            return
        self._start_monitoring()

    def cmd_DISABLE(self, gcmd):
        """Disable crash detection monitoring."""
        self._stop_monitoring()
        gcmd.respond_info("TMC4671 crash detection: DISABLED")

    def cmd_STATUS(self, gcmd):
        """Report current position errors for all monitored axes."""
        if not self.tmc_objects:
            gcmd.respond_info("No TMC4671 drivers configured")
            return

        gcmd.respond_info(
            "TMC4671 Crash Detection Status:\n"
            "  Monitoring: %s\n"
            "  Threshold: %d counts\n"
            "  Consecutive errors required: %d"
            % ("ACTIVE" if self.is_monitoring else "INACTIVE",
               self.error_threshold,
               self.consecutive_required))

        for stepper_name in self.tmc_objects:
            error = self._get_position_error(stepper_name)
            counter = self.error_counters.get(stepper_name, 0)
            if error is not None:
                status = "OK" if error < self.error_threshold else "WARNING"
                gcmd.respond_info(
                    "  %s: error=%d counts [%s] "
                    "(consecutive=%d/%d)"
                    % (stepper_name, error, status,
                       counter, self.consecutive_required))
            else:
                gcmd.respond_info(
                    "  %s: UNABLE TO READ (check SPI)" % stepper_name)


def load_config(config):
    """Klipper module entry point."""
    return TMC4671CrashDetect(config)
