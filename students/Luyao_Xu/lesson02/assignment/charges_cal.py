"""
Returns total price paid for individual rentals
"""
import argparse
import json
from datetime import datetime
import math
import logging


def parse_cmd_arguments():
    """
    Parse arguments for script.
    :return: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-i', '--input', help='input JSON file', required=True)
    parser.add_argument('-o', '--output', help='ouput JSON file', required=True)
    parser.add_argument('-d', '--debug', help='debugging log level',
                        required=False, default='0')

    return parser.parse_args()


def get_logger(level='0'):
    """
    Initialize a logger.
    :param level: Logging verbosity level
    :return: Logger obj
    """

    log_format = "%(asctime)s %(filename)s:" \
                 "%(lineno)-3d %(levelname)s %(message)s"
    log_file_name = f'{datetime.now().strftime("%Y-%m-%d")}.log'

    formatter = logging.Formatter(log_format)
    file_handler = logging.FileHandler(log_file_name)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    if level == '0':
        logger.setLevel(logging.CRITICAL)

    if level == '1':
        logger.setLevel(logging.ERROR)
        file_handler.setLevel(logging.ERROR)
        stream_handler.setLevel(logging.ERROR)

    if level == '2':
        logger.setLevel(logging.WARNING)
        file_handler.setLevel(logging.WARNING)
        stream_handler.setLevel(logging.WARNING)

    if level == '3':
        logger.setLevel(logging.DEBUG)
        # do not write debug logs to log file.
        file_handler.setLevel(logging.WARNING)
        stream_handler.setLevel(logging.DEBUG)

    return logger


def load_rentals_file(filename):
    """
    Load input data file.
    :param filename: Data source input file name
    :return: Content of the input file
    """
    with open(filename) as file:
        try:
            return json.load(file)
        except FileNotFoundError:
            logging.error('Input file is not found.')
            exit(0)


def calculate_additional_fields(data):
    """
    Process data by calculating additional fields.
    :param data: Source data
    :return: Processed data
    """
    for value in data.values():
        try:
            rental_start = datetime.strptime(value['rental_start'], '%m/%d/%y')
            rental_end = datetime.strptime(value['rental_end'], '%m/%d/%y')
            value['total_days'] = (rental_end - rental_start).days
            if value['total_days'] < 0:
                raise ValueError('Start date is later than end date.')
            value['total_price'] = value['total_days'] * value['price_per_day']
            value['sqrt_total_price'] = math.sqrt(value['total_price'])
            value['unit_cost'] = value['total_price'] / value['units_rented']
        except ValueError as value_error:
            logging.warning(value_error)
            continue
        except KeyError as key_error:
            msg = f'{str(key_error)} is missing in data point'
            logging.warning(msg)
            continue

    return data


def save_to_json(filename, data):
    """
    Save data to JSON file.
    :param filename: Output path
    :param data: Source data
    :return: None
    """
    with open(filename, 'w') as file:
        try:
            json.dump(data, file)
        except IOError:
            logging.error('Failed to save to output file.')


if __name__ == "__main__":
    ARGS = parse_cmd_arguments()
    _ = get_logger(ARGS.debug)
    logging.debug('Logger is on.')
    RAW_DATA = load_rentals_file(ARGS.input)
    logging.debug('Input file loaded.')
    PROCESSED_DATA = calculate_additional_fields(RAW_DATA)
    logging.debug('Data processed.')
    save_to_json(ARGS.output, PROCESSED_DATA)
    logging.debug('Data saved to local output file.')
