"""
Simple helper functions
"""

import os
import time
import importlib


def get_resource_path():
    package_nm = "llm_analyst.resources"
    module_spec = importlib.util.find_spec(package_nm)
    package_path = os.path.dirname(module_spec.origin)
    return package_path


def pretty_unique_hash():
    mapped_chars = []
    
    digit_map = {
        '00': '0', '01': '1', '02': '2', '03': '3', '04': '4',
        '05': '5', '06': '6', '07': '7', '08': '8', '09': '9',
        '10': 'A', '11': 'B', '12': 'C', '13': 'D', '14': 'E',
        '15': 'F', '16': 'G', '17': 'H', '18': 'I', '19': 'J',
        '20': 'K', '21': 'L', '22': 'M', '23': 'N', '24': 'O',
        '25': 'P', '26': 'Q', '27': 'R', '28': 'S', '29': 'T',
        '30': 'U', '31': 'V', '32': 'W', '33': 'X', '34': 'Y',
        '35': 'Z', '36': 'a', '37': 'b', '38': 'c', '39': 'd',
        '40': 'e', '41': 'f', '42': 'g', '43': 'h', '44': 'i',
        '45': 'j', '46': 'k', '47': 'l', '48': 'm', '49': 'n',
        '50': 'o', '51': 'p', '52': 'q', '53': 'r', '54': 's',
        '55': 't', '56': 'u', '57': 'v', '58': 'w', '59': 'x',
        '60': 'y', '61': 'z', '62': '0', '63': '1', '64': '2',
        '65': '3', '66': '4', '67': '5', '68': '6', '69': '7',
        '70': '8', '71': '9', '72': 'A', '73': 'B', '74': 'C',
        '75': 'D', '76': 'E', '77': 'F', '78': 'G', '79': 'H',
        '80': 'I', '81': 'J', '82': 'K', '83': 'L', '84': 'M',
        '85': 'N', '86': 'O', '87': 'P', '88': 'Q', '89': 'R',
        '90': 'S', '91': 'T', '92': 'U', '93': 'V', '94': 'W',
        '95': 'X', '96': 'Y', '97': 'Z', '98': 'a', '99': 'b'
    }
    timestamp = str(int(time.time()*1000000)) 

    for i in range(0, len(timestamp), 2):
        pair = timestamp[i:i+2]
        mapped_chars.append(digit_map[pair])

    mapped_string = ''.join(mapped_chars)

    return mapped_string
