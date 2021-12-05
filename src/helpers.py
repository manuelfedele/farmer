import datetime
import logging

import msgpack

from src.mappings import mappings

logger = logging.getLogger("farmer")


def map_entity(symbol: str, data: dict, _type: str) -> dict:
    """
    Maps the received entity to the corresponding mapping
    Args:
        symbol: the symbol of the entity
        data: The entity to be mapped
        _type: The type of entity

    Returns:
        The mapped entity

    """
    data['S'] = symbol
    mapping = mappings[_type]
    _mapped_dict = {}
    for key, value in data.items():
        try:
            _key = mapping[key]

            if isinstance(value, msgpack.ext.Timestamp):
                value = value.to_datetime()

            elif isinstance(value, str) and 'time' in _key.lower():
                try:
                    value = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    pass
            _mapped_dict[mapping[key]] = value
        except KeyError:
            logger.debug(f"Key {key} not found in mapping.")
    return _mapped_dict
