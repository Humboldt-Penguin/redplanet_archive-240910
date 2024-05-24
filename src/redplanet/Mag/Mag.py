"""
Written by Zain Kamal (zain.eris.kamal@rutgers.edu).
https://github.com/Humboldt-Penguin/redplanet

For more information, call `help(Mag)` or directly view docstring in `Mag/__init__.py`.

"""



############################################################################################################################################

from redplanet import utils

import pooch

import pyshtools as pysh
import numpy as np




############################################################################################################################################
""" module variables """





__datapath = utils.getPath(pooch.os_cache('redplanet'), 'Mag')
'''
Path where pooch downloads/caches data.
'''









__current_model = {}
'''
Holds all information for the currently loaded crustal thickness model. Fields are:
    - (model parameters)
        - 'grid_spacing'
            - Grid spacing [deg]
    - (data)
        - 'lons'
            - 1D np.ndarray of longitudes [deg]
        - 'lats'
            - 1D np.ndarray of latitudes [deg]
        - 'dat_Bmag'
            - 2D np.ndarray of magnetic field, total magnitude [nT]
        - 'dat_Blon'
            - 2D np.ndarray of magnetic field, longitude/theta/azimuth component [nT]
        - 'dat_Blat'
            - 2D np.ndarray of magnetic field, latitude/phi/elevation component [nT]
        - 'dat_Br'
            - 2D np.ndarray of magnetic field, radial component [nT]
'''

def get_current_model() -> dict:
    return __current_model










############################################################################################################################################
""" initialize (run upon import, last line of file) """


def __init():


    '''load the highest resolution of langlais magnetic field model'''
    load_langlais()



    











############################################################################################################################################
""" functions """




def load_langlais(lmax=134):

    '''temporarily disable the logger so we don't get unnecessary output every time a file is downloaded for the first time'''    
    logger = pooch.get_logger()
    logger.disabled = True

    filepath = pooch.retrieve(
        fname      = 'Langlais2019.sh.gz',
        url        = r'https://drive.google.com/file/d/1cm40isnBN4YhSdIYlYHHaExJmoMi_K8Q/view?usp=sharing',
        known_hash = 'sha256:3cad9e268f0673be1702f1df504a4cbcb8dba4480c7b3f629921911488fe247b',
        path       = __datapath,
        downloader = utils.download_gdrive_file,
    )

    logger.disabled = False



    '''construct data'''

    langlais = pysh.SHMagCoeffs.from_file(filepath, lmax=lmax, skip=4, r0=3393.5e3, header=False, file_units='nT', name='Langlais2019', units='nT', encoding='utf-8')

    # langlais_grid = langlais.expand()
    # dat_langlais = langlais_grid.to_xarray()

    dat_langlais = langlais.expand().to_xarray()

    lons = utils.clon2lon(dat_langlais['lon'].to_numpy())
    lats = dat_langlais['lat'].to_numpy()

    dat = {
        'dat_Bmag': dat_langlais['total'].to_numpy(),
        'dat_Blon': dat_langlais['theta'].to_numpy(),
        'dat_Blat': dat_langlais['phi'].to_numpy(),
        'dat_Br': dat_langlais['radial'].to_numpy(),
    }

    
    # rearrange: gridded data is originally in clon 0->360, and we converted to lon, so the current order is lon 0->180/-180->0. we want to convert to lon -180->180, so we rearrange columns.
    i_left = np.where(lons == -180)[0][0]
    lons = np.hstack((lons[i_left:], lons[:i_left]))
    
    # rearrange: make lats increasing
    lats = np.flip(lats)

    # pad: lon (via wraparound) and lat (via duplication) to allow for interpolation at edges
    grid_spacing = 180. / (2 * lmax + 2)
    lons = np.array( (*lons, lons[-1]+grid_spacing, lons[-1]+grid_spacing*2) )
    lats = np.array( (*lats, lats[-1]+grid_spacing) )



    __current_model['grid_spacing'] = grid_spacing
    __current_model['lons'] = lons
    __current_model['lats'] = lats

    # duplicate above changes for 2d data
    for key in dat:
        dat[key] = np.hstack((dat[key][:,i_left:], dat[key][:,:i_left]))
        
        dat[key] = np.flip(dat[key], axis=0)

        dat[key] = np.hstack( (dat[key], dat[key][:,0:2] ) )
        dat[key] = np.vstack( (dat[key], dat[key][-1:,:]) )

        __current_model[key] = dat[key]






    ## manually calculate grid spacing
    # '''get grid spacing'''
    # lon_spacing = np.unique(np.diff(lons).round(3))
    # lat_spacing = np.unique(np.diff(lats).round(3))

    # if len(lon_spacing) > 1:
    #     raise ValueError('lon spacing is not uniform')
    # if len(lat_spacing) > 1:
    #     raise ValueError('lat spacing is not uniform')
    # if abs(lon_spacing) != abs(lat_spacing):
    #     raise ValueError('lon and lat spacing are not equal')
    
    # grid_spacing = lon_spacing[0]




















def get(quantity: str, lon, lat) -> float:
    
    utils.checkCoords(lon, lat)


    match quantity:

        case 'Bmag' | 'B_mag':
            dat = __current_model['dat_Bmag']

        case 'Blon' | 'B_lon' | 'Btheta' | 'B_theta':
            dat = __current_model['dat_Blon']

        case 'Blat' | 'B_lat' | 'Bphi' | 'B_phi':
            dat = __current_model['dat_Blat']

        case 'Br' | 'B_r':
            dat = __current_model['dat_Br']

        case _:
            raise Exception('''Invalid quantity. Options are:
                            "Bmag" | "B_mag",
                            "Blon" | "B_lon" | "Btheta" | "B_theta",
                            "Blat" | "B_lat" | "Bphi" | "B_phi",
                            "Br" | "B_r".''')




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
    i_lat = np.searchsorted(__current_model['lats'], lat, side='right') - 1
    j_lon = np.searchsorted(__current_model['lons'], lon, side='right') - 1


    points = (
        (
            __current_model['lons'][j_lon],
            __current_model['lats'][i_lat],
            dat                    [i_lat, j_lon]
        ),
        (
            __current_model['lons'][j_lon+1],
            __current_model['lats'][i_lat],
            dat                    [i_lat, j_lon+1]
        ),
        (
            __current_model['lons'][j_lon],
            __current_model['lats'][i_lat+1],
            dat                    [i_lat+1, j_lon]
        ),
        (
            __current_model['lons'][j_lon+1],
            __current_model['lats'][i_lat+1],
            dat                    [i_lat+1, j_lon+1]
        ),
    )



    val = bilinear_interpolation(lon, lat, points)

    return val









def visualize(
    quantity: str, 
    lon_bounds = (-180,180), 
    lat_bounds = (-90,90), 
    grid_spacing = 1,
    overlay = ...,
    mask_lower = ...,
    mask_upper = ...,
    mask_range = [-120,120],
    title = ...,
    cbar_title = ...,
    colormap = 'jet',
    transparency_data = ...,
    transparency_mola = ...,
    figsize = ...,
):
    """
    DESCRIPTION:
    ------------
        Create a map of magnetic field TODO.
    

    PARAMETERS:
    ------------
        [Star (*) indicates parameters that are not mandatory, but there's a high likelihood users will want to adjust them.]

        For these parameters, see documentation for `redplanet.Mag.get()` or call `help(redplanet.Mag.get)`.
            quantity
    
        For these parameters, see documentation for `redplanet.utils.visualize()` or call `help(redplanet.utils.visualize)`.
            *lon_bounds
            *lat_bounds
            *grid_spacing
            *overlay
            mask_lower
            mask_upper
            mask_range
            title
            *cbar_title
            colormap
            transparency_data
            transparency_mola
            figsize

    
    NOTES:
    ------------
        Default masking range is (-120,120) nT, inspired by Figure 6 of:
            > Langlais, B., Thébault, E., Houliez, A., Purucker, M. E., & Lillis, R. J. (2019). A new model of the crustal magnetic field of Mars using MGS and MAVEN. Journal of Geophysical Research: Planets, 124, 1542– 1569. https://doi.org/10.1029/2018JE005854

    """


    '''kwargs will hold all arguments passed to `redplanet.utils.visualize()`'''
    kwargs = {}



    '''plotThis is the only mandatory argument for `redplanet.utils.visualize()`'''
    def plotThis(lon, lat):
        return get(quantity, lon, lat)
    
    

    '''default values that can't be defined in function header'''

    title = 'Crustal Magnetic Field at Surface (Langlais et al., 2019)' if title is ... else title

    match quantity:

        case 'Bmag' | 'B_mag':
            cbar_title = r'$|B|$ [nT]' if cbar_title is ... else cbar_title

        case 'Blon' | 'B_lon' | 'Btheta' | 'B_theta':
            cbar_title = r'$B_\theta$ [nT]' if cbar_title is ... else cbar_title

        case 'Blat' | 'B_lat' | 'Bphi' | 'B_phi':
            cbar_title = r'$B_\phi$ [nT]' if cbar_title is ... else cbar_title

        case 'Br' | 'B_r':
            cbar_title = r'$B_r$ [nT]' if cbar_title is ... else cbar_title

        case _:
            raise Exception('''Invalid quantity. Options are:
                            "Bmag" | "B_mag",
                            "Blon" | "B_lon" | "Btheta" | "B_theta",
                            "Blat" | "B_lat" | "Bphi" | "B_phi",
                            "Br" | "B_r".''')




    '''Add all arguments that are either specified by the user or have default values'''
    for key, value in locals().items():
        if value is not ...:
            kwargs[key] = value


    utils.visualize(**kwargs)

    









############################################################################################################################################
__init()