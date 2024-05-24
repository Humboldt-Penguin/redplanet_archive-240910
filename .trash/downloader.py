"""
Written by Zain Kamal (zain.eris.kamal@rutgers.edu).
https://github.com/Humboldt-Penguin/redplanet


...

TODO:
    [ ] 
"""

from pathlib import Path
import pooch


'''basics'''

_dirpath_data_root = pooch.os_cache('redplanet')

def get_data_path():
    return _dirpath_data_root

def set_data_path(path):
    global _dirpath_data_root
    _dirpath_data_root = Path(path)




'''downloading'''


# def download