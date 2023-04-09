# coding=utf-8
import copy
import pydevd_pycharm

from mycodo.inputs.base_input import AbstractInput
from mycodo.config_translations import TRANSLATIONS
from mycodo.databases.models import Conversion
from mycodo.databases.models import InputChannel
from mycodo.utils.database import db_retrieve_table_daemon
from mycodo.utils.influx import add_measurements_influxdb
from mycodo.utils.inputs import parse_measurement

# Measurements
measurements_dict = {}

channels_dict = {
    0: {}
}
# pydevd_pycharm.settrace('192.168.77.4', port=2020, stdoutToServer=True, stderrToServer=True)
# Input information
# See the inputs directory for examples of working modules.
# The following link provides the full list of options with descriptions:
# https://github.com/kizniche/Mycodo/blob/single_file_input_modules/mycodo/inputs/examples/example_all_options_temperature.py
INPUT_INFORMATION = {
    'input_name_unique': 'ARDUINO_SERIAL',
    'input_manufacturer': 'Arduino',
    'input_name': 'Arduino Serial Input',
    'input_name_short': 'Arduino',
    'input_library': 'pyserial',
    'measurements_name': 'Misc.',
    'measurements_dict': measurements_dict,
    'measurements_use_same_timestamp': True,

    'url_manufacturer': 'https://www.arduino.cc/',

    # This allows the user to set how many measurements for this Input and select the measurement units
    'measurements_variable_amount': True,

    # This sets the number of channels to the same quantity of user-set measurements
    'channel_quantity_same_as_measurements': True,

    # For use with Inputs that store multiple measurements.
    # Set True if all measurements should be stored in the database with the same timestamp.
    # Set False to use the timestamp generated when self.value_set() is used to save measurement.
    'measurements_use_same_timestamp': True,

    'options_enabled': [
        'measurements_select',
        'period',
        'pre_output',
        'serial_baud_rate',
        'serial_location'
    ],
    'options_disabled': [
        'interface'
    ],

    'dependencies_module': [
        ('pip-pypi', 'random', 'random') #TODO set dependency
    ],

    'interfaces': ['Serial'],
    'serial_location': '/dev/ttyACM0',
    'serial_baud_rate': 115200,

    'custom_options_message': 'This is a message for custom actions.',
    'custom_options': [
        {
            'id': 'option_one',
            'type': 'integer',
            'default_value': 999,
            'name': 'Option One Value',
            'phrase': 'Value for option one.'
        },
    ],

    'custom_commands_message': 'This is a message for custom actions.',
    'custom_commands': [
        {
            'id': 'reset_arduino_command',
            'type': 'text',
            'default_value': '',
            'name': 'Arduino Reset Command',
            'phrase': 'Command that resets the Arduino'
        },
        {
            'id': 'reset_arduino',
            'type': 'button',
            'name': 'Reset Arduino',
            'phrase': "Resets the Arduino"
        },
        {  # This message will be displayed on a new line
            'type': 'message',
            'default_value': 'Here is another action',
        }
    ],

    'custom_channel_options': [
        {
            'id': 'serial_command',
            'type': 'text',
            'default_value': '',
            'required': True,
            'name': TRANSLATIONS['serial_command']['title'],
            'phrase': TRANSLATIONS['serial_command']['phrase']
        }
    ],

    'channels_dict': channels_dict,
}


class InputModule(AbstractInput):
    """Input support class."""
    def __init__(self, input_dev, testing=False):
        pydevd_pycharm.settrace('192.168.77.2', port=2021, stdoutToServer=True, stderrToServer=True)
        super().__init__(input_dev, testing=testing, name=__name__)
        # Initialize variables
        self.random = None
        self.interface = None
        self.i2c_address = None
        self.i2c_bus = None

        # Initialize custom options from INPUT_INFORMATION
        self.option_one = False

    def initialize(self):
        # Load dependent modules
        import random
        self.random = random


        # Set options that be used elsewhere in this class
        self.interface = self.input_dev.interface
        self.serial_location = self.input_dev.serial_location
        self.serial_baud_rate = self.input_dev.serial_baud_rate

    def get_measurement(self):
        """Measures temperature and humidity."""
        # Resetting these values ensures old measurements aren't mistaken for new measurements
        self.return_dict = copy.deepcopy(measurements_dict)

        # Actual input measurement code
        try:
            input_channels = db_retrieve_table_daemon(
                InputChannel).filter(InputChannel.input_id == self.input_dev.unique_id).all()
            self.options_channels = self.setup_custom_channel_options_json(
                INPUT_INFORMATION['custom_channel_options'], input_channels)
            humidity = -1
            temperature = 0

            self.logger.info("Option one value is {}".format(self.option_one))


            self.logger.info(
                "This INFO message will always be displayed. "
                "Acquiring measurements...")

            if self.is_enabled(0):  # Only store the measurement if it's enabled
                self.value_set(0, temperature)

            if self.is_enabled(1):  # Only store the measurement if it's enabled
                self.value_set(1, humidity)

            # Only store the measurement if measurements 0, 1, and 2 are enabled
            # Since the calculation of measurement 2 depend on measurements 0 and 1
            if (self.is_enabled(2) and
                    self.is_enabled(0) and
                    self.is_enabled(1)):
                dewpoint = 1
                self.value_set(2, dewpoint)

            self.logger.debug(
                "This DEBUG message will only be displayed if the Debug "
                "option is enabled. {}".format(self.return_dict))

            return self.return_dict
        except Exception as msg:
            self.logger.error("Exception: {}".format(msg))

    def button_one(self, args_dict):
        self.logger.error("Button One Pressed!: {}".format(int(args_dict['button_one_value'])))

    def button_two(self, args_dict):
        self.logger.error("Button Two Pressed!: {}".format(int(args_dict['button_two_value'])))
