"""
Written by Zain Kamal (zain.eris.kamal@rutgers.edu).
https://github.com/Humboldt-Penguin/redplanet

For more information, call `help(Craters)` or directly view docstring in `Craters/__init__.py`.

"""



############################################################################################################################################


from redplanet import utils

import pooch

import pandas as pd
import matplotlib.pyplot as plt




############################################################################################################################################
"""module variables"""



__datapath = utils.getPath(pooch.os_cache('redplanet'), 'Craters')
'''
Path where pooch downloads/caches data.
'''




__database: pd.core.frame.DataFrame
'''
Pandas dataframe containing information for all craters. Keys are:
    - 'ID'
    - 'name'
    - 'lat'
    - 'lon'
    - 'diameter_km'
    - 'depth_rimfloor'
    - 'num_layers'
See `get_database()` docstring for more information.
'''


def get_database(minDiam=0, maxDiam=9999, dict=False):
    """
    DESCRIPTION:
    ------------
        Access a full/filtered database of Martian craters with diameter >=10km. 
    
        
    PARAMETERS:
    ------------
        minDiam, maxDiam : float (default 0, 9999)
            Minimum and maximum crater diameters to include in the database. Units are km.

        dict : bool (default False)
            If True, returns a list of dictionaries. If False, returns a pandas dataframe.


    RETURNS:
    ------------
        dict or pandas dataframe
            Keys are: 
            - 'ID'
            - 'name'
            - 'lat'
            - 'lon'
            - 'diameter_km'
            - 'depth_rimfloor'
            - 'num_layers'

            
    REFERENCES:
    ------------
        Crater database:
            > Robbins, S.J., and B.M. Hynek (2012). A New Global Database of Mars Impact Craters ≥1 km: 1. Database Creation, Properties, and Parameters. Journal of Geophysical Research - Planets, 117, E05004. doi: 10.1029/2011JE003966.
            - We actually use a database uploaded to Kaggle in 2021 (https://www.kaggle.com/datasets/codebreaker619/mars-crater-study-dataset?resource=download). There is no associated citation, but it is attributed to Stuart Robbins. The database is nearly identical for craters >10km, with a few minor discrepencies and less columns (which are not used in this module anyway). We take the csv and remove all craters <10km to reduce size, then upload to Google Drive: https://drive.google.com/file/d/1s7I529s9J7E8e3iMTX1s-wXJQnw5nwlm/view?usp=sharing.

    """
    dat = __database[(minDiam <= __database['diameter_km']) & (__database['diameter_km'] <= maxDiam)]
    if dict:
        dat = list(dat.to_dict('index').values())
    return dat




############################################################################################################################################
""" initialize (run upon import, last line of file) """


def __init():

    logger = pooch.get_logger()
    logger.disabled = True


    filepath = pooch.retrieve(
        fname      = 'robbins_crater_database_10kmPlus.csv',
        url        = r'https://drive.google.com/file/d/1s7I529s9J7E8e3iMTX1s-wXJQnw5nwlm/view?usp=sharing',
        known_hash = 'sha256:64cf509527a26fd0ab80b28d747690dd3f253ab53e8dc9c36d5acca65b1e1aea',
        path       = __datapath,
        downloader = utils.download_gdrive_file,
    )
    

    config = [
        ['CRATER_ID', 'ID', str],
        ['CRATER_NAME', 'name', str],
        ['LATITUDE_CIRCLE_IMAGE', 'lat', float],
        ['LONGITUDE_CIRCLE_IMAGE', 'lon', float],
        ['DIAM_CIRCLE_IMAGE', 'diameter_km', float],
        ['DEPTH_RIMFLOOR_TOPOG', 'depth_rimfloor', float],
        ['NUMBER_LAYERS', 'n_layers', int],
    ]


    global __database
    __database = pd.read_csv(
        filepath, 
        usecols=[x[0] for x in config],
        dtype={x[0]: x[2] for x in config}
    ) 
    __database = __database.rename(columns={x[0]: x[1] for x in config})


    logger.disabled = False






############################################################################################################################################
""" functions """



def get(string):
    """
    DESCRIPTION:
    ------------
        Get all information for a crater based on its name or ID. Returns a dictionary with keys:
        - 'ID'
        - 'name'
        - 'lat'
        - 'lon'
        - 'diameter_km'
        - 'depth_rimfloor'
        - 'num_layers'


    """
    
    crater = __database[ __database['name'].str.lower() == string.lower() ]
    if not crater.empty:
        return next(iter(crater.to_dict('index').values()))
    
    crater = __database[ __database['ID'].str.lower() == string.lower() ]
    if not crater.empty:
        return next(iter(crater.to_dict('index').values()))
    
    raise ValueError(f'No crater found with name or ID "{string}".')
    # return False





############################################################################################################################################
__init()