"""
Written by Zain Kamal (zain.eris.kamal@rutgers.edu).
https://github.com/Humboldt-Penguin/redplanet

For more information, call `help(GRS)` or directly view docstring in `GRS/__init__.py`.

...

TODO:
    [ ] Finish writing/fleshing out docstrings. 
    [ ] Add proper units + attributes + citations to xarray dataset. 
    [ ] Write a `plot` function? Need to rewrite the corresponding `visualize` function in `redplanet.utils` first (rename to `plot` there as well). 

"""


from redplanet import utils

from pathlib import Path

import pooch
import numpy as np
import pandas as pd 
import xarray as xr








## see `_initialize()`.
_has_been_initialized = False

## path where pooch downloads/caches data.
dirpath_data_root = pooch.os_cache('redplanet')

## holds GRS data in xarray or dictionary format.
_dat_grs_xarr = None
_dat_grs_dict = None


def get_rawdata(how=None):
    """
    `format` options: ['xarray', 'dict']

    Note: when viewing/exploring dictionaries, it may help to call:
        ```
        from redplanet import utils
        utils.print_dict(dat_grs_dict)     # insert any dictionary here
        ```
    """
    if how is None:
        raise ValueError('Options are ["xarray", "dict"].')
    
    _initialize()
    match how:
        case 'xarray':
            return _dat_grs_xarr
        case 'dict':
            return _dat_grs_dict
        case _:
            raise ValueError('Options are ["xarray", "dict"].')










def _initialize():
    """
    DESCRIPTION:
    ------------
        Download data (or load from cache) and format into xarray `_dat_grs` and dictionary `_dat_grs_dict`.
    
    REFERENCES:
    ------------
        2022_Mars_Odyssey_GRS_Element_Concentration_Maps:
            > Rani, A., Basu Sarbadhikari, A., Hood, D. R., Gasnault, O., Nambiar, S., & Karunatillake, S. (2022). 2001 Mars Odyssey Gamma Ray Spectrometer Element Concentration Maps. https://doi.org/10.1029/2022GL099235
            - Data downloaded from https://digitalcommons.lsu.edu/geo_psl/1/
            - Data mirrored to Google Drive for significantly increased downloading speeds

    """


    '''lazy initialization uwu'''
    
    """NOTE: See 'Footnote 1' at bottom of `GRS.py` for self-note justifying `global` variables and modules over classes."""
    
    global _has_been_initialized
    if _has_been_initialized:
        return
    
    global _dat_grs_xarr, _dat_grs_dict



    '''download data files (if not already)'''
    with utils.disable_pooch_logger():
        fpaths_rawdat = pooch.retrieve(
            fname      = '2022_Mars_Odyssey_GRS_Element_Concentration_Maps.zip',
            url        = r'https://drive.google.com/file/d/1Z5Esv-Y4JAQvC84U-VataKJHIJ9OA4_8/view?usp=sharing',
            known_hash = 'sha256:45e047a645ae8d1bbd8e43062adab16a22786786ecb17d8e44bfc95f471ff9b7',
            path       = dirpath_data_root / 'GRS',
            downloader = utils.download_gdrive_file,
            processor  = pooch.Unzip(),
        )
    fpaths_rawdat = [Path(f) for f in fpaths_rawdat if 'README_EBH_SK_AR_SK.txt' not in f]



    '''load data into xarray'''
    dfs = []
    for fpath_rawdat in fpaths_rawdat:
        element = fpath_rawdat.stem.split('_')[0].lower()

        df = pd.read_csv(
            fpath_rawdat, 
            sep='\s+', 
            na_values=9999.999, 
            header=0, 
            usecols=[0, 1, 2, 3], 
            names=['lat', 'lon', 'concentration', 'sigma']
        )

        if element == 'th':
            scale_factor = 0.000001  # correct given "ppm" to concentration out of 1
        else: 
            scale_factor = 0.01      # correct "weight percent" to concentration out of 1
        df[['concentration','sigma']] *= scale_factor

        df['element'] = element
        dfs.append(df)

    all_dfs = pd.concat(dfs)

    ## pre-compute volatiles array for speed/convenience
    volatiles_df = all_dfs[all_dfs['element'].isin(['cl', 'h2o', 's'])]
    volatiles_sum = volatiles_df.groupby(['lat', 'lon']).sum(min_count=3).reset_index()
    volatiles_sum['element'] = 'volatiles'
    dfs.append(volatiles_sum)
    all_dfs = pd.concat(dfs)

    ## tbh not sure about ideal indexing order lolz
    # _dat_grs = xr.Dataset.from_dataframe(all_dfs.set_index(['lat', 'lon', 'element']))
    # _dat_grs = xr.Dataset.from_dataframe(all_dfs.set_index(['element', 'lon', 'lat']))
    _dat_grs_xarr = xr.Dataset.from_dataframe(all_dfs.set_index(['element', 'lat', 'lon'])) 

    _dat_grs_xarr.attrs = {
        'units': 'concentration out of 1',
        'grid_spacing': 5,
    }



    '''load data into dictionary as well for speedy manual indexing'''
    _dat_grs_dict = {
        'lats': _dat_grs_xarr.lat.values,
        'lons': _dat_grs_xarr.lon.values,
        'attrs': _dat_grs_xarr.attrs,
    }
    
    for element in _dat_grs_xarr.element.values:
        _dat_grs_dict[element] = {}
        for data_var in list(_dat_grs_xarr.data_vars):
            _dat_grs_dict[element][data_var] = _dat_grs_xarr.sel(element=element)[data_var].values



    '''lazy loadinggg'''
    _has_been_initialized = True
    return








def get_pt(
    element, 
    lon, 
    lat, 
    quantity = 'concentration', 
    normalize = False, 
):
    """
    DESCRIPTION:
    ------------
        Get GRS-derived concentration/sigma of an element *at a desired coordinate*. For large regions (more than 10^5 points), use `get_region`. 
    
    
    PARAMETERS:
    ------------
        *element : str
            - Element for which you want to make a global concentration map. Options are ['al','ca','cl','fe','h2o','k','si','s','th']. 
        
        *lon : float 
            - Longitude coordinate, choose one: 
                - 'lon'  in range [-180, 180] (Arabia Terra in middle). 
                - 'clon' in range [0, 360] (Arabia Terra at edges). 
            (this is mostly preference, only functional difference is when you want to wraparound.)
        
        *lat : float
            - Latitude coordinate in range [-90, 90]. 
        
        quantity : str (default 'concentration')
            - Quantity to plot. Options are ['concentration', 'sigma'].
        
        normalize : bool (default False)
            - If True, normalize to a volatile-free (Cl, H2O, S) basis.
                > "For such measurement [from GRS] to represent the bulk chemistry of the martian upper crust, it must be normalized to a volatile-free basis (22). That equates to a 7 to 14% increase in the K, Th, and U abundances (22), which we applied to the chemical maps by renormalizing to Cl, stoichiometric H2O, and S-free basis."
                Source: "Groundwater production from geothermal heating on early Mars and implication for early martian habitability", Ojha et al. 2020, https://www.science.org/doi/10.1126/sciadv.abb1669

            
    RETURN:
    ------------
        float or nan:
            - Surface concentration of an element at the desired coordinate, or nan if undefined in GRS data. 
                - Units are in concentration out of one (i.e. original wt% * 0.01 or ppm * 0.000001). 

    """

    '''checks'''
    _initialize()

    if element not in ['al','ca','cl','fe','h2o','k','si','s','th']:
        raise ValueError(f"Element {element} is not in list of supported elements: ['al','ca','cl','fe','h2o','k','si','s','th'].")
    
    if not (-180 <= lon <= 360):
        raise ValueError(f'Given longitude coordinate {lon=} is out of range [-180, 360].')
    if not (-90 <= lat <= 90):
        raise ValueError(f'Given latitude coordinate {lat=} is out of range [-90, 90].')
    
    lon = utils.clon2lon(lon) # this only modifies values btwn 180 and 360
    


    '''accessing'''

    """NOTE: See 'Footnote 2' at bottom of `GRS.py` for explanation of this indexing method."""
    
    index_nearest_lat = _dat_grs_dict['lats'].shape[0] - np.argmin(np.flip(np.abs(_dat_grs_dict['lats'] - lat))) - 1
    index_nearest_lon = _dat_grs_dict['lons'].shape[0] - np.argmin(np.flip(np.abs(_dat_grs_dict['lons'] - lon))) - 1    
    
    val = _dat_grs_dict[element][quantity][index_nearest_lat][index_nearest_lon] 

    if normalize:
        if element in ['cl','h2o','s']:
            raise ValueError(f"Can't normalize a volatile element ('{element}') to a volatile-free (cl, h2o, s) basis.")
        val_volatiles = _dat_grs_dict['volatiles'][quantity][index_nearest_lat][index_nearest_lon]
        val = val/(1-val_volatiles)

    return val










def get_region(
    element, 
    lons         = None,
    lats         = None,
    lon_bounds   = None, 
    lat_bounds   = None, 
    grid_spacing = None,
    num_points   = None, 
    quantity     = 'concentration',
    normalize    = False, 
    as_xarray    = False,
):
    """
    lon_bounds, clon_bounds, lat_bounds : tuple(float, float)
        - Bounding box for data swath. 

    grid_spacing : float
        - Spacing between points being sampled in degrees. Note that original data is 5x5 degree bins.

    note: force the user to define their own `lons`/`lats` values so they can input it to multiple modules (GRS,Crust,etc.) and ultimately encourage them to do calculation via numpy arrays which is significantly faster than manual loop iterating.
    """


    '''args     (this approach is a bit verbose, but easy to understand and comprehensive)'''

    error_msg = 'Invalid inputs for `get_region`. Options are: [1] `lons=..., lats=...` OR [2] `lon_bounds=..., lat_bounds=..., grid_spacing=...` OR [3] `lon_bounds=..., lat_bounds=..., num_points=...`.'
    ## input case 1:
    if ((lons is not None) and (lats is not None)):
        ## eliminate case 2:
        if ((lon_bounds is not None) or (lat_bounds is not None) or (grid_spacing is not None) or (num_points is not None)):
            raise ValueError(error_msg)
        ## execution:
        pass
    ## input case 2:
    elif ((lon_bounds is not None) and (lat_bounds is not None)):
        ## eliminate case 1:
        if ((lons is not None) or (lats is not None)):
            raise ValueError(error_msg)
        ## execution (based on `grid_spacing` xor `num_points`):
        if ((grid_spacing is not None) and (num_points is None)):
            lons = np.arange(lon_bounds[0], lon_bounds[1]+grid_spacing, grid_spacing)
            lats = np.arange(lat_bounds[0], lat_bounds[1]+grid_spacing, grid_spacing)
        elif ((grid_spacing is None) and (num_points is not None)):
            lons = np.linspace(lon_bounds[0], lon_bounds[1], num_points)
            lats = np.linspace(lat_bounds[0], lat_bounds[1], num_points)
        else:
            raise ValueError(error_msg + ' (HINT: Specify either `grid_spacing` OR `num_points`, but not both.)')

    

    '''checks'''
    _initialize()

    if element not in ['al','ca','cl','fe','h2o','k','si','s','th']:
        raise ValueError(f"Element {element} is not in list of supported elements: ['al','ca','cl','fe','h2o','k','si','s','th'].")
    
    if np.any(lons < -180) or np.any(lons > 360):
        raise ValueError(f'One value in given `lons` array is out of range [-180, 360].')
    if np.any(lats < -90) or np.any(lats > 90):
        raise ValueError(f'One value in given `lats` array is out of range [-90, 90].')
    
    lons = utils.clon2lon(lons) # this only modifies values btwn 180 and 360
    
    ## If you don't round, then xarray (`get_region`) and numpy indexing (`get_pt`) methods will give different answers in response to numpy arrays due to floating point imprecision. For some reason I'm not fully sure why. Took me probably 3 hours to figure that out.
    lons = np.round(lons, 10)
    lats = np.round(lats, 10)
    


    '''accessing'''

    arr = _dat_grs_xarr.sel(element=element).sel(lon=lons, lat=lats, method='nearest')[quantity]

    if normalize:
        if element in ['cl','h2o','s']:
            raise ValueError(f"Can't normalize a volatile element ('{element}') to a volatile-free (cl, h2o, s) basis.")
        arr_volatiles = _dat_grs_xarr.sel(element='volatiles').sel(lon=lons, lat=lats, method='nearest')[quantity]
        arr = arr/(1-arr_volatiles)

    if as_xarray == False:
        arr = arr.values

    return arr








'''
[FOOTNOTE 1]

Note to future self:
    - I've been debating for a while whether `GRS.py` and similar should be written as: 
        1. classes (i.e. explicitly declared with `class GRS():`, but forced to be singletons with decorators and `cls` method args), or 
        2. modules (i.e. just a script with definitions that can be imported as you wish, effectively a singleton instance). 
    - I settled on the latter since there's no reason to want multiple instances for most of these data accessing classes, it'll just add confusion and force the user to write unnecessary code. 
        i. Reservation: "Performing data-loading operations when importing is bad practice." 
            --> Solution: Lazy-loading, see `_has_data_been_loaded` variable in this module. 
        ii. Reservation: "You're creating too many useless folders for `GRS/GRS.py`, `Crust/Crust.py`, etc." 
            --> Solution: That's not a problem, it's functionally advantageous because it's easier to extend in the future, and aesthetically I prefer this structure since it appears much more neat. Also there are major packages that do this too so no big deal. 
        iii. Reservation: "I'm forcing myself to declare global variables, that's bad practice!" 
            --> Solution: Globals aren't always bad! You should understand their strengths and weaknesses and judge in the context of the specific task you're working on. Consider an excerpt from this short article/blog/essay "Global Variables Are OK, and In Fact Necessary" by Prof. Norm Matloff: https://heather.cs.ucdavis.edu/matloff/public_html/globals.html
                > "But much more significantly, the same people who make the above objection mysteriously have no problem with "global" use of member variables in object-oriented languages. A member variable in a class is accessible to all member functions in the class. In other words, the variable is "global" to all the functions in the class. If a member function accesses the member variable directly, i.e. not via parameters, then this is exactly the same situation that the "anti-globalists" decry."
            .... If I believe that `GRS.py` is better suited to be a module than a class due to singleton/template reasoning, but my only reservations/drawback is that I can't declare global variables in modules like I can do with classes, then I'm being a bozo! I *CAN* declare global variables in modules just like I would in a class -- my reluctancy is purely motivated by hearing and internalizing dogma. 
'''


'''
[FOOTNOTE 2]

- Consider this problem:
    - "Given a value (lon/lat) and an array (lons/lats), find the index (index_nearest_lon/lat) of the array element which is closest to the given value."

- There are two implementations to solve this...
    (1) 
        ```
        index_nearest_lat = np.argmin(np.abs(dat_grs_dict['lats'] - lat))
        ```
    (2) 
        ```
        index_nearest_lat = _dat_grs_dict['lats'].shape[0] - np.argmin(np.flip(np.abs(_dat_grs_dict['lats'] - lat))) - 1
        ```

- **The only difference** between the two implementations is, in the case of a *tie*, the first method chooses the lower index, and the second method chooses the higher index. We choose the latter because xarray's `sel` function with `method='nearest'` always chooses the higher index and we want consistent behavior here. 
'''