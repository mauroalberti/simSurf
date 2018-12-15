
from typing import Dict

import yaml


def read_yaml(file_pth: str) -> Dict:

    with open(file_pth, 'r') as stream:
        data = yaml.safe_load(stream)

    return data

