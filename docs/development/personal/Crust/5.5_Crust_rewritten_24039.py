"""
Written by Zain Kamal (zain.eris.kamal@rutgers.edu).
https://github.com/Humboldt-Penguin/redplanet

For more information, call `help(Crust)` or directly view docstring in `Crust/__init__.py`.

...

TODO:
    [ ] Finish writing/fleshing out docstrings. 
    [ ] Add proper units + attributes + citations to xarray dataset. 
    [ ] Write a `plot` function? Need to rewrite the corresponding `visualize` function in `redplanet.utils` first (rename to `plot` there as well). 

"""


from redplanet import utils

from pathlib import Path
import json

import pooch
import numpy as np
import pandas as pd
import xarray as xr
import pyshtools as pysh






## lazy initialization.
_has_been_initialized = False

## path where pooch downloads/caches data.
_datapath = pooch.os_cache('redplanet') / 'Crust'

## holds Crust data in xarray dataset or dictionary format.
dat_crust_xrds = None
dat_crust_dict = None

dat_dichotomy_coords = None



def get_rawdata(how=None):
    """
    `format` options: ['xarray', 'dict', 'dichotomy']

    Note: when viewing/exploring dictionaries, it may help to call:
        ```
        from redplanet import utils
        utils.print_dict(dat_something_dict)     # insert any dictionary here
        ```
    """
    if how is None:
        raise ValueError('Options are ["xarray", "dict", "dichotomy"].')

    _initialize()
    match how:
        case 'xarray':
            return dat_crust_xrds
        case 'dict':
            return dat_crust_dict
        case 'dichotomy':
            return dat_dichotomy_coords
        case _:
            raise ValueError('Options are ["xarray", "dict", "dichotomy"].')



def get_model_info():
    return {
        'name': dat_crust_xrds.attrs.get('moho_model_name'), 
        'RIM': dat_crust_xrds.attrs.get('moho_model_RIM'), 
        'insight_thickness': dat_crust_xrds.attrs.get('moho_model_insight_thickness'), 
        'rho_north': dat_crust_xrds.attrs.get('moho_model_rho_north'), 
        'rho_south': dat_crust_xrds.attrs.get('moho_model_rho_south'), 
    }












def _initialize():

    '''lazy initialization uwu'''
    global _has_been_initialized
    if _has_been_initialized:
        return

    '''load topo+dichotomy only -- user should consciously think about which moho to choose, rather than getting an arbitrary model for free'''


    def _load_dichotomy():

        global dat_dichotomy_coords

        '''download / cache dichotomy coords'''
        with utils.disable_pooch_logger():
            fpath_dichotomy_coords = pooch.retrieve(
                fname      = 'dichotomy_coordinates-JAH-0-360.txt',
                url        = r'https://drive.google.com/file/d/17exPNRMKXGwa3daTEBN02llfdya6OZJY/view?usp=sharing',
                known_hash = 'sha256:42f2b9f32c9e9100ef4a9977171a54654c3bf25602555945405a93ca45ac6bb2',
                path       = _datapath / 'dichotomy',
                downloader = utils.download_gdrive_file,
            )
        fpath_dichotomy_coords = Path(fpath_dichotomy_coords)

        '''load into Nx2 numpy array of dichotomy coordinates, structured (lon, lat).'''
        dat_dichotomy_coords = np.loadtxt(fpath_dichotomy_coords)

        ## fix the lons (convert from `0->360` to `0->180 U -180->0` and sort)
        dat_dichotomy_coords[:,0] = utils.clon2lon(dat_dichotomy_coords[:,0])
        dat_dichotomy_coords = dat_dichotomy_coords[np.argsort(dat_dichotomy_coords[:,0])]

        ## add wraparound coordinates for safety / convenience
        dat_dichotomy_coords = np.vstack((
            dat_dichotomy_coords, 
            [dat_dichotomy_coords[0,0]+360, dat_dichotomy_coords[0,1]], 
            [dat_dichotomy_coords[1,0]+360, dat_dichotomy_coords[1,1]], 
        ))



    _load_dichotomy()
    # load_topo()

    '''lazy loadinggg'''
    _has_been_initialized = True

    return












def is_above_dichotomy(lon, lat):

    _initialize()

    i_lon = np.searchsorted(dat_dichotomy_coords[:,0], lon, side='right') - 1
    llon, llat = dat_dichotomy_coords[i_lon]
    rlon, rlat = dat_dichotomy_coords[i_lon+1]

    tlat = llat + (rlat-llat)*( (lon-llon)/(rlon-llon) )
    return lat >= tlat

    # v1 = (rlon-llon, rlat-llat)
    # v2 = (rlon-lon, rlat-lat)
    # xp = v1[0]*v2[1] - v1[1]*v2[0]  # cross product magnitude
    # return xp >= 0









def load_topo(grid_spacing=0.1): #, maximum_degree=None):

    _initialize()

    global dat_crust_xrds


    ## too annoying to write this out, and not even that important, maybe figure this out later.
    # '''args handling'''
    # if ((grid_spacing is None) and (maximum_degree is None)):
    #     raise ValueError('Must provide either `grid_spacing` or `maximum_degree` (neither was provided).')
    # elif ((grid_spacing is not None) and (maximum_degree is not None)):
    #     raise ValueError('Must provide *either* `grid_spacing` or `maximum_degree` (not both).')
    # elif ((grid_spacing < 0.035) or (maximum_degree > 2600)):
    #     raise ValueError('Input resolution exceeds maximum resolution of our spherical harmonic model (must have `grid_spacing >= 0.035` or `maximum_degree <= 2600`).')


    # '''format inputs'''
    # if (grid_spacing is not None):
    #     lmax = round(90. / grid_spacing - 1)
    #     grid_spacing = 180. / (2 * lmax + 2)
    # else:
    #     lmax = maximum_degree
    #     grid_spacing = 180. / (2 * lmax + 2)
        


    lmax = round(90. / grid_spacing - 1)
    grid_spacing = 180. / (2 * lmax + 2)


    '''load topography'''

    if grid_spacing == 0.1:
        '''OPTION 1/2: use pre-computed grid for speed -- see 'Footnote 1' at bottom of `Crust.py` for further discussion on this.'''
        with utils.disable_pooch_logger():
            fpath_topo_grid = pooch.retrieve(
                fname      = 'pysh-ShGrid_MarsTopo2600_0.1deg_km.npy',
                url        = r'https://drive.google.com/file/d/10m0S4eunb05jkOf4rwnxiWAToLVpt1hq/view?usp=sharing',
                known_hash = 'sha256:1a7e7fdfc23b8b8d68c115469888fcf304957ec681ebe12295d7e8cef31feb61',
                path       = _datapath / 'topo',
                downloader = utils.download_gdrive_file,
            )

        # topo_grid = Path(topo_grid)  # causes error when trying to readfile with pysh.SHCoeffs.from_file, it expects a string
        topo_shgrid = pysh.SHGrid.from_file(fpath_topo_grid, binary=True)


    else:
        '''OPTION 2/2: if user is manually requesting a finer grid, compute manually -- the overhead is downloading additional ~300MB to cache and 3-10 seconds processing, so recommend avoiding this.'''
        with utils.disable_pooch_logger():
            fpath_MarsTopo2600 = pooch.retrieve(
                fname      = 'MarsTopo2600.shape.gz',
                url        = r'https://drive.google.com/file/d/1so3sGXNzdYkTdpzjvOxwYBsvr1Y1lwXt/view?usp=sharing',
                known_hash = 'sha256:8882a9ee7ee405d971b752028409f69bd934ba5411f1c64eaacd149e3b8642af',
                path       = _datapath / 'topo',
                downloader = utils.download_gdrive_file,
                processor  = pooch.Decompress(),
            )

        # fpath_MarsTopo2600 = Path(fpath_MarsTopo2600)  # causes error when trying to readfile with pysh.SHCoeffs.from_file, it expects a string
        topo_shcoeffs = pysh.SHCoeffs.from_file(fpath_MarsTopo2600, lmax=lmax, name='MarsTopo2600', units='m')
        topo_shgrid = topo_shcoeffs.expand(grid='DH2', extend=True) * 1e-3 # convert m -> km



    '''format into xarray dataset'''
    topo_xrda = _fix_xarray_coords(topo_shgrid.to_xarray())
    dat_crust_xrds = xr.Dataset({'topo': topo_xrda})
    dat_crust_xrds.attrs = {
        'units': 'km',
        'grid_spacing': grid_spacing, 
        'lmax': lmax,
        'topo_model': 'MarsTopo2600',
    }


    _update_dict_to_match_xrds()







def load_model(
    RIM, 
    insight_thickness, 
    rho_north, 
    rho_south, 
    suppress_model_error = False,
) -> bool:

    _initialize()


    global dat_crust_xrds
    
    model_name = f'{RIM}-{insight_thickness}-{rho_south}-{rho_north}'



    '''load a pre-computed registry of moho models, which provides a google drive download link and a sha256 hash for a given model name'''
    with utils.disable_pooch_logger():
        fpath_moho_shcoeffs_registry = pooch.retrieve(
            fname      = 'Crust_mohoSHcoeffs_rawdata_registry.json',
            url        = r'https://drive.google.com/file/d/17JJuTFKkHh651-rt2J2eFKnxiki0w4ue/view?usp=sharing',
            known_hash = 'sha256:1800ee2883dc6bcc82bd34eb2eebced5b59fbe6c593cbc4e9122271fd01c1491',
            path       = _datapath / 'moho', 
            downloader = utils.download_gdrive_file,
        )

    with open(fpath_moho_shcoeffs_registry, 'r') as file:
        moho_shcoeffs_registry = json.load(file)



    '''download SH coefficients for the chosen model'''
    try:
        _ = moho_shcoeffs_registry[model_name]
    except KeyError:
        if suppress_model_error:
            return False
        else:
            raise ValueError(f'No Moho model with the inputs {model_name} exists.')

    with utils.disable_pooch_logger():
        fpath_moho_shcoeffs = pooch.retrieve(
            fname      = f'{model_name}.txt',
            url        = moho_shcoeffs_registry[model_name]['link'], 
            known_hash = moho_shcoeffs_registry[model_name]['hash'],
            path       = _datapath / 'moho' / 'SH_coeffs', 
            downloader = utils.download_gdrive_file, 
        )



    '''load+save model'''
    lmax = dat_crust_xrds.lmax
    moho_shcoeffs = pysh.SHCoeffs.from_file(fpath_moho_shcoeffs)
    moho_shgrid = moho_shcoeffs.expand(lmax=lmax, grid='DH2', extend=True) * 1e-3 # convert m -> km

    moho_xrda = _fix_xarray_coords(moho_shgrid.to_xarray())
    dat_crust_xrds['moho'] = moho_xrda
    more_moho_attrs = {
        'moho_model_name': model_name,
        'moho_model_RIM': RIM,
        'moho_model_insight_thickness': insight_thickness,
        'moho_model_rho_north': rho_north,
        'moho_model_rho_south': rho_south,
    }
    dat_crust_xrds.attrs.update(more_moho_attrs)


    _update_dict_to_match_xrds()

    return True









def _fix_xarray_coords(dataarray):
    dataarray = dataarray.sel(lon=slice(0,359.99999))   # Artiface of pyshtools `extend=True` thing, but I don't just flip it to False because that would clip out latitude -90 as well.
    dataarray = dataarray.assign_coords(lon=xr.apply_ufunc(utils.clon2lon, dataarray.lon))
    dataarray = dataarray.sortby('lon', ascending=True)
    dataarray = dataarray.sortby('lat', ascending=True)
    dataarray = xr.concat([dataarray, dataarray.sel(lon=-180).assign_coords(lon=180)], dim='lon')  # wraparound for interpolation
    return dataarray







def _update_dict_to_match_xrds():
    global dat_crust_dict
    dat_crust_dict = {
        'lats': dat_crust_xrds.lat.values,
        'lons': dat_crust_xrds.lon.values,
        'attrs': dat_crust_xrds.attrs, 
    }
    for data_var in list(dat_crust_xrds.data_vars):
        dat_crust_dict[data_var] = dat_crust_xrds[data_var].values














def get_pt(
    quantity, 
    lon, 
    lat, 
    interpolate = False,
):

    '''checks'''
    _initialize()

    if not (-180 <= lon <= 360):
        raise ValueError(f'Given longitude coordinate {lon=} is out of range [-180, 360].')
    if not (-90 <= lat <= 90):
        raise ValueError(f'Given latitude coordinate {lat=} is out of range [-90, 90].')
    
    lon = utils.clon2lon(lon) # this only modifies values btwn 180 and 360



    '''accessing'''
    if interpolate:
        method = 'linear'
    else:
        method = 'nearest'

    match quantity:

        case 'topo' | 'moho':
            val = dat_crust_xrds.interp(lon=lon, lat=lat, assume_sorted=True, method=method)[quantity].item()
        
        case 'crust' | 'crustal thickness' | 'crthick':
            interped = dat_crust_xrds.interp(lon=lon, lat=lat, assume_sorted=True, method=method)
            val = (interped.topo - interped.moho).item()
        
        case 'rho' | 'density' | 'crustal density':
            if is_above_dichotomy(lon, lat):
                val = get_model_info()['rho_north']
            else:
                val = get_model_info()['rho_south']
        
        case _:
            raise Exception('Invalid quantity. Options are ["topo", "moho", "crust"/"crustal thickness"/"crthick", "rho"/"density"/"crustal desntiy"].')

    return val











def get_region(
    quantity, 
    lons         = None,
    lats         = None,
    lon_bounds   = None, 
    lat_bounds   = None, 
    grid_spacing = None,
    num_points   = None, 
    interpolate  = False,
    as_xarray    = False,
):
    """
    lon_bounds, clon_bounds, lat_bounds : tuple(float, float)
        - Bounding box for data swath. 

    grid_spacing : float
        - Spacing between points being sampled in degrees. Note that original data is 5x5 degree bins.

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

    if np.any(lons < -180) or np.any(lons > 360):
        raise ValueError(f'One value in given `lons` array is out of range [-180, 360].')
    if np.any(lats < -90) or np.any(lats > 90):
        raise ValueError(f'One value in given `lats` array is out of range [-90, 90].')
    
    lons = np.round(lons, 10)
    lats = np.round(lats, 10)
    
    lons = utils.clon2lon(lons) # this only modifies values btwn 180 and 360



    '''accessing'''
    if interpolate:
        method = 'linear'
    else:
        method = 'nearest'

    match quantity:

        case 'topo' | 'moho':
            arr = dat_crust_xrds.interp(lon=lons, lat=lats, assume_sorted=True, method=method)[quantity]
        
        case 'crust' | 'crustal thickness' | 'crthick':
            interped = dat_crust_xrds.interp(lon=lons, lat=lats, assume_sorted=True, method=method)
            arr = (interped.topo - interped.moho)
        
        case 'rho' | 'density' | 'crustal density':
            vec_is_above_dichotomy = np.vectorize(is_above_dichotomy)
            arr = vec_is_above_dichotomy(np.meshgrid(lons, lats)[0], np.meshgrid(lons, lats)[1])
            arr = np.where(arr, get_model_info()['rho_north'], get_model_info()['rho_south'])
        
        case _:
            raise Exception('Invalid quantity. Options are ["topo", "moho", "crust"/"crustal thickness"/"crthick", "rho"/"density"/"crustal density"].')


    if as_xarray == False:
        arr = arr.values

    return arr









'''
[FOOTNOTE 1]

- Manually loading topography is slightly inconvenient:
    - Spherical harmonic coefficient file 'MarsTopo2600.shape.gz' is 73MB compressed, or 200MB decompressed. 
    - Loading this and expanding to 0.1 degree grid spacing takes 3-7 seconds, which can be annoying for users if forced to wait everytime they import `redplanet.Crust`. 
- So instead, I pre-compute the `pysh.ShGrid` object and save it to a numpy binary for speed -- corresponding code is below. This topography grid is loaded by default, and if the user wants a finer resolution, we download/load/expand manually.

    ```
    from redplanet import utils
    import pyshtools as pysh
    import pooch
    from pathlib import Path

    grid_spacing = 0.1

    lmax = round(90. / grid_spacing - 1)
    grid_spacing = 180. / (2 * lmax + 2)

    with utils.disable_pooch_logger():
        fpath_MarsTopo2600 = pooch.retrieve(
            fname      = 'MarsTopo2600.shape.gz',
            url        = r'https://drive.google.com/file/d/1so3sGXNzdYkTdpzjvOxwYBsvr1Y1lwXt/view?usp=sharing',
            known_hash = 'sha256:8882a9ee7ee405d971b752028409f69bd934ba5411f1c64eaacd149e3b8642af',
            path       = pooch.os_cache('redplanet') / 'Crust',
            downloader = utils.download_gdrive_file,
            processor  = pooch.Decompress(),
        )

    topo_shcoeffs = pysh.SHCoeffs.from_file(fpath_MarsTopo2600, lmax=lmax, name='MarsTopo2600', units='m')
    topo_shgrid = topo_shcoeffs.expand(grid='DH2', extend=True) * 1e-3 # convert m -> km

    fpath = Path.cwd() / 'pysh-ShGrid_MarsTopo2600_0.1deg_km.npy'
    topo_shgrid.to_file(fpath, binary=True)
    print(fpath)
    print(f'sha256:{pooch.file_hash(fpath)}')
    ```

'''