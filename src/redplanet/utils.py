import os

import numpy as np


# '''
# -----------------------------------------------------------------------
# System
# -----------------------------------------------------------------------
# '''


def getPath(*args):
    """
    DESCRIPTION:
    ------------
        Join all arguments into a single path specific to your system. 
            - Use 'current' to get the directory this file (the one calling this function) is in. 
                - NOTE: if you want to get the directory of the file that called the function that called this function, use `os.path.dirname(os.path.abspath('__file__'))`.
            - Use '..' to get the path to parent directory. 

    USAGE:
    ------------
        Example: If you're running a script/notebook in `/src/main/`, you can get the path to `/src/data/foo.txt` with:
            `utils.getPath('current', '..', 'data', 'foo.txt')`            
    """
    args = [os.getcwd() if arg == 'current' else arg for arg in args]
    return os.path.abspath(os.path.join(*args))






# '''
# -----------------------------------------------------------------------
# Coordinates
# -----------------------------------------------------------------------
# '''


# def lon2clon(lon: float) -> float:
#     """
#     Converts longitude value in range [-180,180] to cyclical longitude (aka colongitude) in range [180,360]U[0,180], in degrees.

#     Using longitude [-180,180] puts Arabia Terra in the middle.
#     Using cyclical longitude [0,360] puts Olympus Mons in the middle.

#     """
#     return lon % 360


# def clon2lon(clon: float) -> float:
#     """
#     Converts cyclical longitude (aka colongitude) in range [0,360] to longitude in range [0,180]U[-180,0].

#     Using longitude [-180,180] puts Arabia Terra in the middle.
#     Using cyclical longitude [0,360] puts Olympus Mons in the middle.
#     """
#     return ((clon-180) % 360) - 180


# def lat2cola(lat: float) -> float:
#     """
#     Converts latitude value in range [-90,90] to cyclical latitude (aka colatitude) in range [0,180], in degrees.    
#     """
#     return lat % 180

# def cola2lat(cola: float) -> float:
#     """
#     Converts cyclical latitude (aka colatitude) in range [0,180] to latitude value in range [-90,90], in degrees.    
#     """
#     return ((cola-90) % 180) - 90




# '''
# -----------------------------------------------------------------------
# Misc
# -----------------------------------------------------------------------
# '''


def print_dict(d: dict, indent: int = 0) -> None:
    """
    DESCRIPTION:
    ------------
        Cleaner way to print a dictionary.

    PARAMETERS:
    ------------
        d : dict
        indent : int

    """
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            print_dict(value, indent+1)
        else:
            print('\t' * (indent+1) + str(value))
    return


# def find_nth_substring(haystack, needle, n):
#     parts= haystack.split(needle, n+1)
#     if len(parts)<=n+1:
#         return -1
#     return len(haystack)-len(parts[-1])-len(needle)


# def get_key_by_value(dictionary, value):
#     for key, val in dictionary.items():
#         if val == value:
#             return key
#     return None


# def unique(a):
#     """
#     Return unique values of array a, preserving order. Pandas has an equivalent `pd.unique()` which is faster for large datasets -- this version doesn't require pandas and is fine for small data.
#     """
#     return a[np.sort(np.unique(a, return_index=True)[1])]