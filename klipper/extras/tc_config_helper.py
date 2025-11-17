# Toolchanger Config Helper
# Simple module to save config values from gcode macros
#
# Copyright (C) 2025 PrintStructor
# This file may be distributed under the terms of the GNU GPLv3 license.

class TCConfigHelper:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        
        # Register command
        self.gcode.register_command('TC_SAVE_CONFIG_VALUE',
                                   self.cmd_TC_SAVE_CONFIG_VALUE,
                                   desc=self.cmd_TC_SAVE_CONFIG_VALUE_help)
    
    cmd_TC_SAVE_CONFIG_VALUE_help = "Save a value to config file"
    
    def cmd_TC_SAVE_CONFIG_VALUE(self, gcmd):
        """Save a config value using configfile.set()"""
        section = gcmd.get('SECTION')
        option = gcmd.get('OPTION')
        value = gcmd.get('VALUE')
        
        # Get configfile object and save
        configfile = self.printer.lookup_object('configfile')
        configfile.set(section, option, value)
        
        gcmd.respond_info(f"Saved [{section}] {option} = {value} (use SAVE_CONFIG)")

def load_config(config):
    return TCConfigHelper(config)
