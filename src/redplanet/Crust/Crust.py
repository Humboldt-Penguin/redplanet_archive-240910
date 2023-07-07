"""
Written by Zain Kamal (zain.eris.kamal@rutgers.edu).
https://github.com/Humboldt-Penguin/redplanet

For more information, call `help(Crust)` or directly view docstring in `Crust/__init__.py`.

"""



############################################################################################################################################

# from redplanet import utils

from redplanet import utils

import json

import pooch

import pyshtools as pysh
import numpy as np
import matplotlib.pyplot as plt




############################################################################################################################################
""" module variables """




# dict_RIM = {
#     0: "DWThot",
#     1: "DWThotCrust1",
#     2: "DWThotCrust1r",
#     3: "EH45Tcold",
#     4: "EH45TcoldCrust1",
#     5: "EH45TcoldCrust1r",
#     6: "EH45ThotCrust2",
#     7: "EH45ThotCrust2r",
#     8: "LFAK",
#     9: "SANAK",
#     10: "TAYAK",
#     11: "DWAK",
#     12: "ZG_DW",
#     13: "YOTHotRc1760kmDc40km",
#     14: "YOTHotRc1810kmDc40km",
#     15: "Khan2022",
# }
# dict_RIM.update(dict([reversed(i) for i in dict_RIM.items()]))

# def RIM_toInt(RIM: str) -> int:
#     return dict_RIM[RIM]
# def RIM_toStr(RIM_int: int) -> str:
#     return dict_RIM[RIM_int]








current_model = {}
'''
Holds all information for the currently loaded crustal thickness model. Fields are:
    - (model parameters)
        - 'model_name'
            - f'{RIM}-{insight_thickness}-{rho_south}-{rho_north}'
                - 'RIM'
                    - Reference interior model name (see `dict_RIM` for options)
                - 'insight_thickness'
                    - Seismic thickness at InSight landing site [km]
                - 'rho_north'
                    - Crustal density [kg/m^3] at north of dichotomy
                - 'rho_south'
                    - Crustal density [kg/m^3] at south of dichotomy
        - 'grid_spacing'
            - Grid spacing [deg]
        - 'lmax'
            - Maximum spherical harmonic degree for models
    - (data)
        - 'lats'
            - 1D np.ndarray of latitudes [deg]
        - 'lons'
            - 1D np.ndarray of longitudes [deg]
        - 'dat_topo'
            - 2D np.ndarray of topography [km]
        - `grid_topo`
            - pysh.SHGrid of topography, used to generate thick via `grid_topo - grid_moho`
        - 'dat_moho'
            - 2D np.ndarray of Moho depth [km]
        - 'dat_thick'
            - 2D np.ndarray of crustal thickness [km]
'''
def get_current_model() -> dict:
    selected_keys = ['model_name', 'RIM', 'insight_thickness', 'rho_north', 'rho_south', 'grid_spacing', 'lmax']
    return {key: value for key, value in current_model.items() if key in selected_keys}
    # return current_model







dichotomy_coords: np.ndarray
'''Nx2 np.ndarray of dichotomy coordinates (lon, lat) [deg].'''







############################################################################################################################################
""" initialize (run upon import, last line of file) """


def __init():
    """
    DESCRIPTION:
    ------------
        Download data (or load from cache) for topography and basic moho/thickness model and format.
    
    REFERENCES:
    ------------
        Dichotomy coordinates:
            > Andrews-Hanna, J., Zuber, M. & Banerdt, W. The Borealis basin and the origin of the martian crustal dichotomy. Nature 453, 1212–1215 (2008). https://doi.org/10.1038/nature07011
            - The file itself ('dichotomy_coordinates-JAH-0-360.txt') is downloaded from 
                > Wieczorek, Mark A. (2022). InSight Crustal Thickness Archive [Data set]. Zenodo. https://doi.org/10.5281/zenodo.6477509

    """

    '''temporarily disable the logger so we don't get unnecessary output every time a file is downloaded for the first time'''    
    logger = pooch.get_logger()
    logger.disabled = True


    '''load dichotomy coordinates'''
    filepath = pooch.retrieve(
        fname='dichotomy_coordinates-JAH-0-360.txt',
        url=r'https://drive.google.com/file/d/17exPNRMKXGwa3daTEBN02llfdya6OZJY/view?usp=sharing',
        known_hash='sha256:42f2b9f32c9e9100ef4a9977171a54654c3bf25602555945405a93ca45ac6bb2',
        path=pooch.os_cache('redplanet'),
        downloader=utils.download_gdrive_file,
    )

    global dichotomy_coords
    dichotomy_coords = np.loadtxt(filepath)

    dichotomy_coords[:,0] = utils.clon2lon(dichotomy_coords[:,0])
    edge = np.where(dichotomy_coords[:,0] == -180)[0][0]
    dichotomy_coords = np.vstack((dichotomy_coords[edge:], dichotomy_coords[:edge]))
    dichotomy_coords = np.vstack((dichotomy_coords, (dichotomy_coords[0,0]+360, dichotomy_coords[0,1]), (dichotomy_coords[1,0]+360, dichotomy_coords[1,1]) ))
    

    '''load a basic topography model. grid spacing 0.1 seems to be a good balance of resolution and speed.'''
    load_topo(grid_spacing=0.1)

    '''load a basic moho/thickness model.'''
    load_model(RIM='Khan2022', insight_thickness=39, rho_north=2900, rho_south=2900)




    logger.disabled = False











############################################################################################################################################
""" functions """




def load_topo(grid_spacing=0.1):
    """
    DESCRIPTION:
    ------------
        Loads a basic topography model. This is called automatically upon import, but can be called again if the user wants to change the grid spacing (not recommended). 
        
        We save both a 2d numpy array and a pysh.SHGrid object, which can be used to generate crustal thickness models later on without having to reload topography. 
    
    PARAMETERS:
    ------------
        grid_spacing : float
            Grid spacing between explicit data points [deg] -- anything between this is interpolated.

    REFERENCES:
    ------------
        "MarsTopo2600 is a 2600 degree and order spherical harmonic model of the shape of the planet Mars." - pyshtools documentation        
            > Wieczorek, Mark A. (2015). Spherical harmonic model of the shape of Mars: MarsTopo2600 [Data set]. Zenodo. https://doi.org/10.5281/zenodo.3870922
            The actual file, 'MarsTopo2600.shape.gz', is reuploaded to Google Drive for significantly increased downloading speeds (~10 seconds as opposed to 3 minutes).

        Textbook:
            > Wieczorek, M.A. (2015). Gravity and Topography of the Terrestrial Planets, Treatise on Geophysics, 2nd edition, Oxford, 153-193, doi:10.1016/B978-0-444-53802-4.00169-X.

    """

    lmax = round(90. / grid_spacing - 1)
    grid_spacing = 180. / (2 * lmax + 2)


    filepath = pooch.retrieve(
        fname='MarsTopo2600.shape.gz',
        url=r'https://drive.google.com/file/d/1so3sGXNzdYkTdpzjvOxwYBsvr1Y1lwXt/view?usp=sharing',
        known_hash='sha256:8882a9ee7ee405d971b752028409f69bd934ba5411f1c64eaacd149e3b8642af',
        path=pooch.os_cache('redplanet'),
        downloader=utils.download_gdrive_file,
    )
    topo = pysh.SHCoeffs.from_file(filepath, lmax=lmax, name='MarsTopo2600', units='m', encoding='utf-8')
    topo_grid = topo.expand(grid='DH2', extend=True) / 1.e3


    lons = utils.clon2lon(topo_grid.lons())
    lats = topo_grid.lats()
    dat_topo = topo_grid.to_array()


    i_left = np.where(lons == -180)[0][0]
    lons = np.hstack((lons[i_left:], lons[:i_left]))
    dat_topo = np.hstack((dat_topo[:,i_left:], dat_topo[:,:i_left]))
    lats = np.flip(lats)
    dat_topo = np.flip(dat_topo, axis=0)
    lons = np.array( (*lons, lons[-1]+grid_spacing, lons[-1]+grid_spacing*2) )
    dat_topo = np.hstack( (dat_topo, dat_topo[:,0:2] ) )
    lats = np.array( (*lats, lats[-1]+grid_spacing) )
    dat_topo = np.vstack( (dat_topo, dat_topo[-1:,:]) )


    '''these are saved if the user wants to get/visualize topography without having loaded a crustal thickness model'''
    current_model['dat_topo'] = dat_topo
    current_model['lons'] = lons
    current_model['lats'] = lats

    '''these will help the user load moho/thick models later on without having to reload topography, which takes a few seconds (grid_spacing=0.1 takes ~3.5 seconds)'''
    current_model['grid_spacing'] = grid_spacing
    current_model['lmax'] = lmax
    current_model['grid_topo'] = topo_grid











def peek_models():
    print('A summary of all available models can be found here: https://docs.google.com/spreadsheets/d/1ZDILcSPdbXAFp60VfyC4xTZzdnAVhx_U/edit?usp=sharing&ouid=107564547097010500390&rtpof=true&sd=true.')






def load_model(
    RIM, 
    insight_thickness, 
    rho_north, 
    rho_south, 
    grid_spacing = -1, 
    suppress_model_error = False,
    suppress_grid_error = False,
) -> bool:
    """
    DESCRIPTION:
    ------------
        Load a moho and crustal thickness dataset based on the provided parameters. The data itself comes from a file of spherical harmonic coefficients which are downloaded/cached from a massive Google Drive folder.
        
        A summary of all available models can be found here: https://docs.google.com/spreadsheets/d/1ZDILcSPdbXAFp60VfyC4xTZzdnAVhx_U/edit?usp=sharing&ouid=107564547097010500390&rtpof=true&sd=true.
    
        
    PARAMETERS:
    ------------
        RIM : str
            Reference interior model name. Options are ["DWThot","DWThotCrust1","DWThotCrust1r","EH45Tcold","EH45TcoldCrust1","EH45TcoldCrust1r","EH45ThotCrust2","EH45ThotCrust2r","LFAK","SANAK","TAYAK","DWAK","ZG_DW","YOTHotRc1760kmDc40km","YOTHotRc1810kmDc40km","Khan2022"]
        
        insight_thickness : int
            Predicted crustal thickness beneath the InSight landing site [km].
        
        rho_north, rho_south : int
            Crustal density [kg/m^3] at north and south of dichotomy.
        
        suppress_model_error : bool (default False)
            If no model with the provided parameters exists, raise an error if `suppress_model_error=False` (default), or return False if `suppress_model_error=True`.
        
        suppress_grid_error : bool (default False)
            If you try to load a model with a grid spacing larger than the currently loaded topography model (not recommended), raise an error if `suppress_grid_error=False` (default), else continue if `suppress_grid_error=True`.

        grid_spacing : float (default to `current_model['grid_spacing']` defined by topography model, default 0.1)
            (We highly recommend not changing this value) Grid spacing between explicit data points [deg] -- anything between this is interpolated. This value should only be supplied if you want finer resolution than the current topography model (default 0.1). Be warned, it will take significantly longer to load, and you are limited by the topography's maximum spherical harmonic coefficient limit of 2600 at grid_spacing=0.0346.
        

    RETURN:
    ------------
        bool
            True if model was successfully loaded, False if no model exists for the provided parameters and `suppress_model_error=True`.

            
    REFERENCES:
    ------------
        Raw data (spherical harmonic coefficients for the crust-mantle interface, i.e. Moho, with various parameters) as well as spreadsheet summarizing available models:
            > Wieczorek, Mark A. (2022). InSight Crustal Thickness Archive [Data set]. Zenodo. https://doi.org/10.5281/zenodo.6477509
            - The process of converting this data into the pre-computed registry we use is explained here: https://gist.github.com/Humboldt-Penguin/6f3f6e7e375f68c1368d094b8fdb70f0

        Original paper: 
            > Wieczorek, M. A., Broquet, A., McLennan, S. M., Rivoldini, A., Golombek, M., Antonangeli, D., et al. (2022). InSight constraints on the global character of the Martian crust. Journal of Geophysical Research: Planets, 127, e2022JE007298. https://doi.org/10.1029/2022JE007298

    """


    if grid_spacing == -1:
        grid_spacing = current_model['grid_spacing']


    '''temporarily disable the logger so we don't get unnecessary output every time a file is downloaded for the first time'''
    logger = pooch.get_logger()
    logger.disabled = True



    '''save current model parameters'''
    current_model['RIM'] = RIM
    current_model['insight_thickness'] = insight_thickness
    current_model['rho_north'] = rho_north
    current_model['rho_south'] = rho_south

    model_name = f'{RIM}-{insight_thickness}-{rho_south}-{rho_north}'
    current_model['model_name'] = model_name




    '''load a pre-computed registry, which provides a google drive download link and a sha256 hash for a given model name'''
    filepath = pooch.retrieve(
        fname='Crust_mohoSHcoeffs_rawdata_registry.json',
        url=r'https://drive.google.com/file/d/17JJuTFKkHh651-rt2J2eFKnxiki0w4ue/view?usp=sharing',
        known_hash='sha256:1800ee2883dc6bcc82bd34eb2eebced5b59fbe6c593cbc4e9122271fd01c1491',
        path=pooch.os_cache('redplanet'), 
        downloader=utils.download_gdrive_file,
    )

    with open(filepath, 'r') as file:
        rawdata_registry = json.load(file)





    '''download SH coefficients for the chosen model from pooch'''
    try:
        _ = rawdata_registry[model_name]
    except KeyError:
        if suppress_model_error:
            return False
        else:
            raise ValueError(f'No Moho model with the inputs {model_name} exists.')
    
    filepath_shcoeffs = pooch.retrieve(
        fname=f'{model_name}.txt',
        url=rawdata_registry[model_name]['link'], 
        known_hash=rawdata_registry[model_name]['hash'],
        path=pooch.os_cache('redplanet'), 
        downloader=utils.download_gdrive_file, 
    )



    '''load 3 'grid'-type objects'''

    if grid_spacing > current_model['grid_spacing'] and not suppress_grid_error:
        raise ValueError(f"Provided grid spacing {grid_spacing} is larger than that of the currently loaded topography model, {current_model['grid_spacing']}. It is not recommended to increase grid spacing above 0.1, as you're losing topography resolution but speedups for loading moho models are insignificant (default grid_spacing=0.1 only takes ~0.1 seconds). If you still wish to proceed, provide `suppress_grid_error=True` as a function argument to suppress this error message.")
    elif grid_spacing != current_model['grid_spacing']:
        load_topo(grid_spacing=grid_spacing)


    grid_spacing = current_model['grid_spacing']
    lmax = current_model['lmax']
    topo_grid = current_model['grid_topo']

    moho = pysh.SHCoeffs.from_file(filepath_shcoeffs)
    moho_grid = moho.expand(lmax=lmax, grid='DH2', extend=True) / 1.e3

    thick_grid = topo_grid - moho_grid




    '''convert to numpy arrays (NOTE: THIS IS INDEXED [lat, lon], OPPOSITE OF GRS -- we prefer this way because it's easier to visualize, since array "rows" correspond to latitudes, and `np.hstack`/`np.vstack` are more intuitive). '''
    dat_topo = topo_grid.to_array()
    dat_moho = moho_grid.to_array()
    dat_thick = thick_grid.to_array()

    lons = utils.clon2lon(topo_grid.lons())
    lats = topo_grid.lats()




    '''rearrange: gridded data is originally in clon 0->360, and we converted to lon, so the current order is lon 0->180/-180->0. we want to convert to lon -180->180, so we rearrange columns.'''
    i_left = np.where(lons == -180)[0][0]

    lons = np.hstack((lons[i_left:], lons[:i_left]))
    dat_topo = np.hstack((dat_topo[:,i_left:], dat_topo[:,:i_left]))
    dat_moho = np.hstack((dat_moho[:,i_left:], dat_moho[:,:i_left]))
    dat_thick = np.hstack((dat_thick[:,i_left:], dat_thick[:,:i_left]))



    '''rearrange: flip lats so they're increasing'''
    lats = np.flip(lats)
    dat_topo = np.flip(dat_topo, axis=0)
    dat_moho = np.flip(dat_moho, axis=0)
    dat_thick = np.flip(dat_thick, axis=0)




    '''edge case: lon is actually from -180->179, so we pad to -180->181 VIA *WRAPAROUND* (extra 1 degree on right side is for later bilinear interpolation alg).'''
    lons = np.array( (*lons, lons[-1]+grid_spacing, lons[-1]+grid_spacing*2) )
    dat_topo = np.hstack( (dat_topo, dat_topo[:,0:2] ) )
    dat_moho = np.hstack( (dat_moho, dat_moho[:,0:2] ) )
    dat_thick = np.hstack( (dat_thick, dat_thick[:,0:2] ) )


    '''edge case: lat is actually from -90->90, so we pad to -90->91 VIA *DUPLICATION* (extra 1 degree on top side is for later bilinear interpolation alg).'''
    lats = np.array( (*lats, lats[-1]+grid_spacing) )
    dat_topo = np.vstack( (dat_topo, dat_topo[-1:,:]) )
    dat_moho = np.vstack( (dat_moho, dat_moho[-1:,:]) )
    dat_thick = np.vstack( (dat_thick, dat_thick[-1:,:]) )





    '''save'''
    current_model['lons'] = lons
    current_model['lats'] = lats
    current_model['dat_topo'] = dat_topo
    current_model['dat_moho'] = dat_moho
    current_model['dat_thick'] = dat_thick



    logger.disabled = False


    return True













def __checkCoords(lon: float, lat: float) -> None:
    if not (-180 <= lon <= 180):
        raise ValueError(f'Longitude {lon} is not in range [-180, 180].')
    if not(-90 <= lat <= 90):
        raise ValueError(f'Latitude {lat} is not in range [-90, 90].')




# def getTopo(lon, lat):
#     return get(lon, lat, 'topo')

# def getMoho(lon, lat):
#     return get(lon, lat, 'moho')

# def getThickness(lon, lat):
#     return get(lon, lat, 'thick')








def get(
    quantity: str, 
    lon: float, 
    lat: float
) -> float:
    """
    DESCRIPTION:
    ------------
        Get topography ('topo'), moho elevation ('moho'), crustal thickness ('thick'), or crustal density ('density') at a specific coordinate. Units are km and kg/m^3.
    
        
    PARAMETERS:
    ------------
        quantity : str
            Options are ['topo'/'topography', 'moho', 'thick'/'thickness', 'rho'/'density'].

        lon, lat : float
            Coordinates in degrees, with longitude in range [-180, 180] and latitude in range [-90, 90].

            
    RETURN:
    ------------
        float
            'topo' -> elevation [km]
            'moho' -> elevation [km]
            'thick' -> thickness [km]
            'rho' -> density [kg/m^3]

    """


    __checkCoords(lon, lat)


    match quantity:

        case 'rho' | 'density':
            
            '''find the two nearest dichotomy coordinates by longitude, interpolate between them to find dichotomy latitude `tlat` at the given `lon`, then compare to `lat`.'''
            i_lon = np.searchsorted(dichotomy_coords[:,0], lon, side='right') - 1
            llon, llat = dichotomy_coords[i_lon]
            rlon, rlat = dichotomy_coords[i_lon+1]
            tlat = llat + (rlat-llat)*( (lon-llon)/(rlon-llon) )
            return (current_model['rho_north'] if lat >= tlat else current_model['rho_south'])
        
        case 'topo' | 'topography':
            dat = current_model['dat_topo']
        case 'moho' | 'moho depth':
            dat = current_model['dat_moho']
        case 'thick' | 'thickness':
            dat = current_model['dat_thick']




    def bilinear_interpolation(x: float, y: float, points: list) -> float:
        '''
        Credit for this function: https://stackoverflow.com/a/8662355/22122546

        Interpolate (x,y) from values associated with four points.
        
        points: list
            four triplets:  (x, y, value).
        
        See formula at:  http://en.wikipedia.org/wiki/Bilinear_interpolation
        '''

        points = sorted(points)               # order points by x, then by y
        (x1, y1, q11), (_x1, y2, q12), (x2, _y1, q21), (_x2, _y2, q22) = points

        # if x1 != _x1 or x2 != _x2 or y1 != _y1 or y2 != _y2:
        #     raise ValueError('points do not form a rectangle')
        # if not x1 <= x <= x2 or not y1 <= y <= y2:
        #     raise ValueError('(x, y) not within the rectangle')

        return (q11 * (x2 - x) * (y2 - y) +
                q21 * (x - x1) * (y2 - y) +
                q12 * (x2 - x) * (y - y1) +
                q22 * (x - x1) * (y - y1)
            ) / ((x2 - x1) * (y2 - y1) + 0.0)
    



    '''get longitude and latitude (`np.searchsorted` returns the index at which the point would be inserted, i.e. point to the 'right', which is why we subtract 1 to get the point to the 'left'. earlier, we padded the edges of the data with extra points to allow for wraparound on the right side, so we don't need to worry about edge cases.)'''
    i_lat = np.searchsorted(current_model['lats'], lat, side='right') - 1
    j_lon = np.searchsorted(current_model['lons'], lon, side='right') - 1


    points = (
        (
            current_model['lons'][j_lon],
            current_model['lats'][i_lat],
            dat[i_lat, j_lon]
        ),
        (
            current_model['lons'][j_lon+1],
            current_model['lats'][i_lat],
            dat[i_lat, j_lon+1]
        ),
        (
            current_model['lons'][j_lon],
            current_model['lats'][i_lat+1],
            dat[i_lat+1, j_lon]
        ),
        (
            current_model['lons'][j_lon+1],
            current_model['lats'][i_lat+1],
            dat[i_lat+1, j_lon+1]
        ),
    )



    val = bilinear_interpolation(lon, lat, points)

    return val














def visualize(
    quantity: str, 
    lon_bounds: tuple = (-180,180), 
    lat_bounds: tuple = (-90,90),  
    grid_spacing: float = 1,
    colormap=''
) -> None:
    """
    DESCRIPTION:
    ------------
        Create a map of topography ('topo'), moho elevation ('moho'), crustal thickness ('thick'), or crustal density ('density'). Model name is formatted f'{Reference_Interior_Model}-{insight_thickness}-{rho_south}-{rho_north}'.
    
        
    PARAMETERS:
    ------------
        quantity : str
            Options are ['topo'/'topography', 'moho', 'thick'/'thickness', 'rho'/'density'].

        lon_bounds, lat_bounds : tuple(2 floats) (default entire map)
            Bounding box for visualization. Longitude in range [-180, 180], latitude in range [-87.5, 87.5].
        
        grid_spacing : float (default to 1)
            Spacing between "pixels" in degrees. Note that smaller resolutions will take longer to plot.
        
        colormap : str (defaults defined at `match quantity:`)
            Colormap to use. See https://matplotlib.org/stable/tutorials/colors/colormaps.html for options.

    """

    lon_left, lon_right = lon_bounds
    lat_bottom, lat_top = lat_bounds

    __checkCoords(lon_left, lat_bottom)
    __checkCoords(lon_left, lat_top)
    __checkCoords(lon_right, lat_bottom)
    __checkCoords(lon_right, lat_top)



    match quantity:
        case 'rho' | 'density':
            title = f'Crustal Density with Model {current_model["model_name"]}'
            cbar_title = 'Density [kg/m$^3$]'
            colormap = 'viridis_r' if colormap == '' else colormap

        case 'topo' | 'topography':
            title = 'Topography'
            cbar_title = 'Elevation [km]'
            colormap = 'binary_r' if colormap == '' else colormap
        
        case 'moho' | 'moho depth':
            title = f'Moho with Model {current_model["model_name"]}'
            cbar_title = 'Elevation [km]'
            colormap = 'magma' if colormap == '' else colormap
        
        case 'thick' | 'thickness':
            title = f'Crustal Thickness with Model {current_model["model_name"]}'
            cbar_title = 'Thickness [km]'
            colormap = 'viridis' if colormap == '' else colormap
            

    '''
    *** If adapting visualization function, modify this function ***
    '''
    def plotThis(lon, lat):
        val = get(quantity, lon, lat)
        return val



    dat = [[
        plotThis(lon,lat)
        for lon in np.arange(lon_left, lon_right, grid_spacing)]
        for lat in np.arange(lat_bottom, lat_top, grid_spacing)]

    '''apply mask'''
    dat = np.asarray(dat)
    # dat = np.ma.masked_where((dat < 0), dat)
    # dat = np.ma.masked_where((dat == get_nanval()), dat)

    '''primary plot'''
    fig = plt.figure(figsize=(10,7))
    ax = plt.axes()
    im = ax.imshow(dat[::-1], cmap=colormap, extent=[lon_left, lon_right, lat_bottom, lat_top])




    '''titles'''
    ax.set_title(title)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    '''axis formatter'''
    ax.xaxis.set_major_formatter('{x}$\degree$')
    ax.yaxis.set_major_formatter('{x}$\degree$')


    # (aesthetic preference)
    if lon_bounds == (-180,180):
        x_spacing = 60
        ax.set_xticks(np.linspace(lon_left, lon_right, int((lon_right-lon_left)/x_spacing)+1))

    if lat_bounds == (-90,90):
        y_spacing = 30
        ax.set_yticks(np.linspace(lat_bottom, lat_top, int((lat_top-lat_bottom)/y_spacing)+1))


    '''x ticks'''
    '''Option 1: Set the spacing between x ticks'''
    # x_spacing = 60
    # ax.set_xticks(np.linspace(lon_left, lon_right, int((lon_right-lon_left)/x_spacing)+1))
    '''Option 2: Set the number of x ticks'''
    # x_ticks = 7
    # ax.set_xticks(np.linspace(lon_left, lon_right, x_ticks))

    '''y ticks'''
    '''Option 1: Set the spacing between y ticks'''
    # y_spacing = 25
    # ax.set_yticks(np.linspace(lat_bottom, lat_top, int((lat_top-lat_bottom)/y_spacing)+1))
    '''Option 2: Set the number of y ticks'''
    # y_ticks = 7
    # ax.set_yticks(np.linspace(lat_bottom, lat_top, y_ticks))


    '''color bar'''
    cax = fig.add_axes([ax.get_position().x1+0.02,ax.get_position().y0,0.02,ax.get_position().height])
    cbar = plt.colorbar(im, cax=cax)
    cbar.set_label(f'{cbar_title}', y=0.5)

    plt.show()













############################################################################################################################################
__init()