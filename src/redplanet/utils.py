import os
import sys

import gdown

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




def download_gdrive_file(url, output_file, pooch):
    '''Helper for `pooch.retrieve` to allow for downloading from Google Drive.'''
    gdown.download(url, output_file, quiet=True, fuzzy=True)




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


def clon2lon(clon: float) -> float:
    """
    Converts cyclical longitude (aka colongitude) in range [0,360] to longitude in range [0,180]U[-180,0].

    Using longitude [-180,180] puts Arabia Terra in the middle.
    Using cyclical longitude [0,360] puts Olympus Mons in the middle.
    """
    return ((clon-180) % 360) - 180


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


def print_dict(d: dict, indent=0, format_pastable=False) -> None:
    """
    DESCRIPTION:
    ------------
        Cleaner way to print a dictionary.

    PARAMETERS:
    ------------
        d : dict
        indent : int
        format_pastable : bool
            If True, will format the output so that it can be pasted into a python script as an assignment to a variable.

    """
    if format_pastable:
        for key, value in d.items():
            spacing = '\t' * indent
            if isinstance(value, dict):
                print(f"{spacing}'{key}': {{")

                # Recursively print the nested dictionary
                print_dict(value, indent+1, format_pastable)

                print(f"{spacing}}},")
            else:
                print(f"{spacing}'{key}': '{value}',")
    else:
        for key, value in d.items():
            print('\t' * indent + str(key))
            if isinstance(value, dict):
                print_dict(value, indent+1, format_pastable)
            else:
                print('\t' * (indent+1) + str(value))





def indexOf(haystack, needle, n=0):
    parts = haystack.split(needle, n+1)
    if len(parts)<=n+1:
        return -1
    return len(haystack)-len(parts[-1])-len(needle)



def size(var):
    variable_size = sys.getsizeof(var) / (1024 * 1024)  # Replace 'your_variable' with the variable you want to measure
    print(f"Variable size: {variable_size} MB")


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