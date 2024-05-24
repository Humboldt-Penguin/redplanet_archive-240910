import sys
import contextlib
# import os

import pooch
import gdown

import numpy as np
import xarray as xr
# import matplotlib.pyplot as plt
# import PIL






''' ######################################################################## '''
'''                             pooch downloading                            '''
''' ######################################################################## '''



def download_gdrive_file(url, output_file, pooch, quiet=True):
    '''Helper for `pooch.retrieve` to allow for downloading from Google Drive.'''
    gdown.download(url, output_file, quiet=quiet, fuzzy=True)


def download_gdrive_file_SHOWPROGRESS(url, output_file, pooch):
    '''Same as `download_gdrive_file`, but shows download progress from `gdown` with `tqdm`.'''
    download_gdrive_file(url, output_file, pooch, quiet=False)






@contextlib.contextmanager
def disable_pooch_logger():
    try:
        pooch.get_logger().disabled = True
        yield
    finally:
        pooch.get_logger().disabled = False




    

## maybe revisit in the future?
# def preload(*args):
#     """
#     DESCRIPTION:
#     ------------
#         Download large files in advance (usually done during module intitialization) and save to cache to speed up later loading. More information about each file downloaded found in respecting module, this is just a shortcut.
    
#     PARAMETERS:
#     ------------
#         args : list[str]
#             Choose options from ['GRS', 'Crust']. If empty, default to all.

#     """

#     if len(args) == 0:
#         args = ['GRS', 'Crust']

#     ... # deleted everything bc clutter and old links










''' ######################################################################## '''
'''                     generic/everyday helper functions                    '''
''' ######################################################################## '''





def indexOf(haystack, needle, n=0):
    """
    Finds the n-th occurrence of a substring (needle) in a string (haystack).

    This function searches for the 'n'th occurrence of a specified substring ('needle') 
    within a given string ('haystack'). If the 'needle' is found, it returns the index 
    at which the 'needle' begins. If the 'needle' is not found or there are fewer than 
    'n' occurrences, it returns -1.

    Parameters:
    haystack (str): The string to be searched.
    needle (str): The substring to find within the haystack.
    n (int, optional): The occurrence number of the 'needle' to find. Defaults to 0, 
                       which corresponds to the first occurrence.

    Returns:
    int: The index of the beginning of the 'n'th occurrence of 'needle' in 'haystack', 
         or -1 if the 'needle' is not found or occurs fewer than 'n+1' times.
    """
    parts = haystack.split(needle, n+1)
    if len(parts)<=n+1:
        return -1
    return len(haystack)-len(parts[-1])-len(needle)










def fix_pyshtools_coords(da : xr.DataArray) -> xr.DataArray:
    '''
    Helper function that converts and reorders an xarray's longitude coordinate ("lon") from positive (0->360) to signed (-180->180), removing any duplicated longitude bands. 
        - This is intended to be used on an instance of the `pyshtools.SHCoeffs` class, upon which you've called `.expand(grid='DH2', extend=True).to_xarray()`. 

    (Explanation)
        - Whenever we have an instance of the `pyshtools.SHCoeffs` class, calling `.expand(grid='DH2', extend=True)` (specifically with the `expand=True` argument) will add values at longitude 360 (I believe this is a duplicate of longitude 0, but I forgot whether I 100% verified this) and latitude -90 (I think this is unique?). For more info on this, import pyshtools and run `help(pyshtools.SHCoeffs.expand)`. 
            - The latter is obviously desired, but the former being a duplicate creates issues when we convert the longitude values from "positive" (0->360) to "signed" (-180->180) using `redplanet.utils.plon2slon` — specifically, since 360 was initially a duplicate of 0, we end up with duplicate coordinates/data at longitude 180 which creates an error when accessing values. We can't just switch `extend=False` because we would lose the value at latitude -90. 
        => THEREFORE, this function first removes the longitude band at 360 (presumed to be a duplicate), then converts/reorders the coordinates/data from positive longitude to signed longitude. 
    '''
    da = da.sel(lon=slice(0,359.99999))
    da = da.assign_coords(lon=xr.apply_ufunc(plon2slon, da.lon))
    da = da.sortby('lon', ascending=True)
    da = da.sortby('lat', ascending=True)
    da = xr.concat([da, da.sel(lon=-180).assign_coords(lon=180)], dim='lon')  # wraparound for interpolation
    return da











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




# def getPath(*args):
#     """
#     ***USE PATHLIB INSTEAD, IT'S GOOD NOW!!!!!***
#         - I initially made this because `os` module had disgusting syntax for paths, but pathlib is cleaner.

#     DESCRIPTION:
#     ------------
#         Join all arguments into a single path specific to your system. 
#             - Use 'current' to get the directory this file (the one calling this function) is in. 
#                 - NOTE: if you want to get the directory of the file that called the function that called this function, use `os.path.dirname(os.path.abspath('__file__'))`.
#             - Use '..' to get the path to parent directory. 

#     USAGE:
#     ------------
#         Example: If you're running a script/notebook in `/src/main/`, you can get the path to `/src/data/foo.txt` with:
#             `utils.getPath('current', '..', 'data', 'foo.txt')`            
#     """
#     args = [os.getcwd() if arg == 'current' else str(arg) for arg in args]
#     return os.path.abspath(os.path.join(*args))











''' ######################################################################## '''
'''                        geospatial helper functions                       '''
''' ######################################################################## '''



''' —————————————————————————————— coordinates ————————————————————————————— '''



def plon2slon(plon: float) -> float:
    """
    Converts "positive" longitude in range [0,360] to "signed"/"standard" longitude in range [0,180]U[-180,0].

    (self reminder:)
        - signed lon   [-180,180]  -->  Arabia Terra in middle.
        - positive lon [   0,360]  -->  Olympus Mons in middle.
    """
    return ((plon-180) % 360) - 180







def clon2lon(clon: float) -> float:
    """
    A long time ago I referred to coordinate axes with -180->180 as "longitude"/"lon", and 0->360 as "colongitude"/"cyclical longitude"/"clon". That's completely wrong but I kept the shorthand for personal code. Now I'm switching to "signed longitude"/"slon" and "positive longitude"/"plon". It's a stupid name but atleast it's not completely incorrect. 
    """
    
    print("DEPRACATION WARNING: Switch from `clon2lon` to `plon2slon`.")

    return plon2slon(clon)







'''
self note, other formulas are:
    - slon2plon
        - slon % 360

    (not sure about these other ones tbh lol)
        - lat2cola
            - lat % 180
        - cola2lat
            - ((cola-90) % 180) - 90
'''










''' ——————————————————————————————— distances —————————————————————————————— '''



def km2theta(km: float) -> float:
    """
    *** NOTE: REPLACE THIS WITH GEODESIC CODE (SEE MY OLD OFFSHORE WIND FARM SAR ANALYSIS CODES) ***
        - (although it's cute how "efficient" (careless) I used to be lol)

    ...

    Rough conversion from kilometers to degrees for getting the longitude/latitude bounds of a crater based on its diameter. 

    We get this equation by by looking at many craters on JMars/QGIS and estimating the angular separation between the left and right edges. We then plot this against diameter in km and then finding the line of best fit, which is linear. Rough calculations here: 
    https://docs.google.com/spreadsheets/d/1Ylr_Oowq_jV1KNXEGuSvXbWNbPZNGUQF1jjv2eTC7Jg/edit?usp=sharing
    
    """
    theta = 0.0185*km - 0.123
    return theta


# def theta2km(theta: float) -> float:
#     km = (theta+0.123)/0.0185
#     return km










''' ——————————————————————————— misc (depracated) —————————————————————————— '''

# def linspace(coord1, coord2, num_points=100):
#     '''
#     Similar to numpy.linspace, but for `(lon,lat)` coordinates (returns evenly spaced coordinates from start point to end point). 
#     '''
#     lon1, lat1 = coord1
#     lon2, lat2 = coord2
#     coords = np.array([np.linspace(lon1, lon2, num_points), np.linspace(lat1, lat2, num_points)]).T
#     return coords


# def arange(coord1, coord2, deg_spacing=1):
#     '''
#     Similar to numpy.arange, but for `(lon,lat)` coordinates (returns evenly spaced coordinates from start point to end point). 
#     '''
#     lon1, lat1 = coord1
#     lon2, lat2 = coord2
#     distance = np.sqrt((lon2 - lon1)**2 + (lat2 - lat1)**2)
#     num_points = int(np.floor(distance / deg_spacing)) + 1
#     return linspace(coord1, coord2, num_points)












''' ######################################################################## '''
'''                    debugging / inspection / aesthetics                   '''
''' ######################################################################## '''



def print_dict(d: dict, indent=0, format_pastable=False, condense_arrays=True) -> None:
    """
    DESCRIPTION:
    ------------
        Cleaner way to print a dictionary, with option to condense numpy arrays.

    PARAMETERS:
    ------------
        d : dict
            The dictionary to print.
        indent : int
            The current indentation level.
        format_pastable : bool
            (Default False) If True, will format the output so that it can be directly pasted into Python code as an assignment to a variable. 
        condense_arrays : bool
            (Default True) If True, condenses numpy arrays into a shape descriptor rather than printing each element. 
    """
    for key, value in d.items():
        spacing = '\t' * indent
        key_repr = f"'{key}'" if isinstance(key, str) else key
        if isinstance(value, dict):
            print(f"{spacing}{key_repr}")
            print_dict(value, indent+1, format_pastable, condense_arrays)
        elif isinstance(value, np.ndarray) and condense_arrays:
            print(f"{spacing}{key_repr}")
            print(f"{spacing}\t<np.ndarray, shape={value.shape}>")
        elif format_pastable:
            value_repr = f"'{value}'" if isinstance(value, str) else value
            print(f"{spacing}{key_repr}: {value_repr!r},")
        else:
            value_repr = f"'{value}'" if isinstance(value, str) else value
            print(f"{spacing}{key_repr}")
            print(f"{spacing}\t{value_repr}")






def size(var):
    """
    Calculates and prints the size of a given variable in megabytes.

    This function takes a variable ('var') and calculates its size using Python's built-in 
    `sys.getsizeof` function. It then converts this size from bytes to megabytes and prints 
    the result. This can be useful for memory management, especially when working with 
    large data structures or in environments with limited memory resources.

    Note: The reported size is the size of the object in memory and does not necessarily 
    reflect its actual size when stored in a file or transmitted over a network.

    Parameters:
    var (any): The variable whose size is to be measured.

    Prints:
    A statement indicating the size of the variable in megabytes.
    """
    variable_size = sys.getsizeof(var) / (1024 * 1024)
    print(f"Variable size: {variable_size} MB")

















''' ######################################################################## '''
'''                           Plotting (depracated)                          '''
''' ######################################################################## '''



pass



# __filepath_mola = ''
# '''
# Only try to download the mola map if the user calls `GRS.visualize()` with `overlay=True`.
# '''


# # def checkCoords(lon, lat):
# #     if not (-180 <= lon <= 180):
# #         raise ValueError(f'Longitude {lon} is not in range [-180, 180].')
# #     if not (-90 <= lat <= 90):
# #         raise ValueError(f'Latitude {lat} is not in range [-90, 90].')



# def visualize(
#     plotThis,
#     lon_bounds = (-180,180), 
#     lat_bounds = (-90,90), 
#     grid_spacing = 1,
#     overlay = False,
#     mask_lower = None,
#     mask_upper = None,
#     mask_range = None,
#     title = None,
#     cbar_title = None,
#     colormap = 'viridis',
#     transparency_data = 0.6,
#     transparency_mola = 0.9,
#     figsize = (10,7),
#     **kwargs,
# ):
#     """
#     DESCRIPTION:
#     ------------
#         Make a well-formatted plot of some quantity over the surface of Mars. 
    

#     PARAMETERS:
#     ------------
#         plotThis : function
#             Function whose arguments are longitude and latitude and returns a value to be plotted. A minimal example:
#                 ```python
#                 def plotThis(lon, lat):
#                     return Crust.get('topography', lon, lat)
#                 ```

#         lon_bounds, lat_bounds : 2-tuple of floats (default entire map)
#             Bounding box for visualization. Longitude in range [-180, 180], latitude in range [-90, 90].

#         grid_spacing : float (default 5 degrees)
#             Spacing between "pixels" in degrees. Note that original data is 5x5 degree bins, so anything smaller than that will be interpolated. Also note that smaller resolutions will take longer to plot.
        
#         overlay : bool (default False)
#             If True, overlay a transparent MOLA map on top of the GRS map. Note that this will take longer to plot.

#         mask_lower, mask_upper : float (default None, None)
#             Any data below/above this value will be masked out.

#         mask_range : tuple(2 floats) (default None)
#             Any data within this range will be masked out. Useful for redplanet.Mag.

#         title, cbar_title : str (default None)
#             Title of plot / colorbar.
        
#         colormap : str (default 'viridis')
#             Colormap to use. See https://matplotlib.org/stable/tutorials/colors/colormaps.html for options.

#         transparency_data, transparency_mola : float (default 0.6, 0.9)
#             Assuming overlay=True, set transparency of the data or MOLA map from a value between 0 (transparent) and 1 (opaque).

#         figsize : (float, float) (default (10,7))
#             Width, height in inches. 


#     REFERENCES:
#     ------------
#         'Mars_HRSC_MOLA_BlendShade_Global_200mp_v2_resized-7.tif'
#             > Fergason, R.L, Hare, T.M., & Laura, J. (2017). HRSC and MOLA Blended Digital Elevation Model at 200m. Astrogeology PDS Annex, U.S. Geological Survey.
#             - Original download link: https://astrogeology.usgs.gov/search/map/Mars/Topography/HRSC_MOLA_Blend/Mars_HRSC_MOLA_BlendShade_Global_200mp_v2
#             - The original file is 5 GB which is unnecessarily high resolution. We downsample the file by reducing the width/height by a factor of 7. Maps with other reduction factors as well as the code to do so can be found here: https://drive.google.com/drive/u/0/folders/1SuURWNQEX3xpawN6a-LEWIduoNjSVqAF.

#     """


#     lon_left, lon_right = lon_bounds
#     lat_bottom, lat_top = lat_bounds



#     checkCoords(lon_left, lat_bottom)
#     checkCoords(lon_left, lat_top)
#     checkCoords(lon_right, lat_bottom)
#     checkCoords(lon_right, lat_top)




#     '''dataset to be plotted'''
#     dat = [[
#         plotThis(lon,lat)
#         for lon in np.arange(lon_left, lon_right, grid_spacing)]
#         for lat in np.arange(lat_bottom, lat_top, grid_spacing)]
    

    
#     '''apply mask'''
#     dat = np.asarray(dat)
#     if mask_lower is not None:
#         dat = np.ma.masked_where((dat < mask_lower), dat)
#     if mask_upper is not None:
#         dat = np.ma.masked_where((dat > mask_upper), dat)
#     if mask_range is not None:
#         dat = np.ma.masked_where((mask_range[0] < dat) & (dat < mask_range[1]), dat)
    



#     '''plotting'''
#     fig = plt.figure(figsize=figsize)
#     ax = plt.axes()



#     '''mola overlay'''
#     if overlay:

#         global __filepath_mola

#         if __filepath_mola == '':
#             logger = pooch.get_logger()
#             logger.disabled = True

#             __filepath_mola = pooch.retrieve(
#                 fname      = 'Mars_HRSC_MOLA_BlendShade_Global_200mp_v2_resized-7.tif',
#                 url        = r'https://drive.google.com/file/d/1i278DaeaFCtY19vREbE35OIm4aFRKXiB/view?usp=sharing',
#                 known_hash = 'sha256:93d32f9b404b7eda1bb8b05caa989e55b219ac19a005d720800ecfe6e2b0bb6c',
#                 path       = getPath(pooch.os_cache('redplanet'), 'Maps'),
#                 downloader = download_gdrive_file
#             )
            
#             logger.disabled = False


#         PIL.Image.MAX_IMAGE_PIXELS = 116159282 + 1 # get around PIL's "DecompressionBombError: Image size (-n- pixels) exceeds limit of 89478485 pixels, could be decompression bomb DOS attack." error

#         mola = PIL.Image.open(__filepath_mola)

#         width, height = mola.size

#         left = ( (lon_left+180) / 360 ) * width
#         right = ( (lon_right+180) / 360 ) * width
#         top = ( (-lat_top+90) / 180 ) * height          # lat values are strange because PIL has (0,0) at the top left. don't think too hard about it, this works.
#         bottom = ( (-lat_bottom+90) / 180 ) * height

#         mola = mola.crop((left, top, right, bottom))

#         im_mola = ax.imshow(mola, cmap='gray', extent=[lon_left, lon_right, lat_bottom, lat_top], alpha=transparency_mola)

#         im_dat = ax.imshow(dat[::-1], cmap=colormap, extent=[lon_left, lon_right, lat_bottom, lat_top], alpha=transparency_data)
#     else:
#         im_dat = ax.imshow(dat[::-1], cmap=colormap, extent=[lon_left, lon_right, lat_bottom, lat_top])






#     '''titles'''
#     if title is not None:
#         ax.set_title(title, pad=9.0)



    
#     ax.set_xlabel('Longitude')
#     ax.set_ylabel('Latitude')

#     ax.xaxis.set_major_formatter('{x}$\degree$')
#     ax.yaxis.set_major_formatter('{x}$\degree$')





#     # (minor aesthetic point: if plotting a global map, ensure that end points are included)
#     if lon_bounds == (-180,180):
#         x_spacing = 60
#         ax.set_xticks(np.linspace(lon_left, lon_right, int((lon_right-lon_left)/x_spacing)+1))

#     if lat_bounds == (-90,90):
#         y_spacing = 30
#         ax.set_yticks(np.linspace(lat_bottom, lat_top, int((lat_top-lat_bottom)/y_spacing)+1))




#     '''x ticks'''
#     '''Option 1: Set the spacing between x ticks'''
#     # x_spacing = 60
#     # ax.set_xticks(np.linspace(lon_left, lon_right, int((lon_right-lon_left)/x_spacing)+1))
#     '''Option 2: Set the number of x ticks'''
#     # x_ticks = 7
#     # ax.set_xticks(np.linspace(lon_left, lon_right, x_ticks))

#     '''y ticks'''
#     '''Option 1: Set the spacing between y ticks'''
#     # y_spacing = 25
#     # ax.set_yticks(np.linspace(lat_bottom, lat_top, int((lat_top-lat_bottom)/y_spacing)+1))
#     '''Option 2: Set the number of y ticks'''
#     # y_ticks = 7
#     # ax.set_yticks(np.linspace(lat_bottom, lat_top, y_ticks))



#     '''color bar'''
#     cax = fig.add_axes([ax.get_position().x1+0.02,ax.get_position().y0,0.02,ax.get_position().height])
#     cbar = plt.colorbar(im_dat, cax=cax)
#     if cbar_title is not None:
#         cbar.set_label(f'{cbar_title}', y=0.5)


#     plt.show()





