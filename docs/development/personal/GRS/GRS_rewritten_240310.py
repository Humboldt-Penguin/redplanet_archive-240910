"""
Written by Zain Kamal (zain.eris.kamal@rutgers.edu).
https://github.com/Humboldt-Penguin/redplanet

For more information, call `help(GRS)` or directly view docstring in `GRS/__init__.py`.

"""



############################################################################################################################################

from redplanet import utils

import pooch
import numpy as np

import os
# import inspect




############################################################################################################################################
""" module variables """



__datapath = utils.getPath(pooch.os_cache('redplanet'), 'GRS')
'''
Path where pooch downloads/caches data.
'''







__nanval: float = -1e10
'''
Value given to pixels where data is not defined (i.e. "NOT_APPLICABLE_CONSTANT"). In the data, this is 9999.999.
We choose an extremely large negative value so we can easily filter/mask it when using the data or plotting. This errs on the side of caution.
'''

def get_nanval() -> float:
    return __nanval








__grid_spacing = 5 # degrees

__lat_range        = np.arange(-87.5 , 87.5   *1.0001, __grid_spacing)
__lat_range_ext    = np.arange(-92.5 , 92.5   *1.0001, __grid_spacing)

__lon_range        = np.arange(-177.5, 177.5  *1.0001, __grid_spacing)
__lon_range_ext    = np.arange(-182.5, 182.5  *1.0001, __grid_spacing)
'''
We opt to hardcode these values in the case of GRS because it's static. It's not hard to programmatically calculate these values in other cases -- the code for such is included but commented out below.
'''








__meta_dat: dict = {}
'''
`meta_dat` is formatted as `meta_dat[element_name][quantity]`, where
    - `element_name` is from ['al','ca','cl','fe','h2o','k','si','s','th']
    - `quantity` is from:
        - 'concentration' = Concentration of the element. 
        - 'sigma' = The error associated with the concentration measurement. 

Calling `meta_dat` as such returns a 2D numpy array containing the original dataset where all units are in concentration out of one (i.e. original wt% * 0.01 or ppm * 0.000001). For some index [i,j], `i` is longitude from `__lon_range[0]` to `__lon_range[-1]`, and `j` is latitude from `__lat_range[0]` to `__lat_range[-1]`.
'''


def get_meta_dat() -> dict:
    return __meta_dat









############################################################################################################################################
""" initialize (run upon import) """





'''download data (or access from cache) and load into `__meta_dat`'''
def __init() -> None:
    """
    DESCRIPTION:
    ------------
        Download data (or load from cache) and format into usable dictionary `__meta_dat`.
    
    REFERENCES:
    ------------
        2022_Mars_Odyssey_GRS_Element_Concentration_Maps:
            > Rani, A., Basu Sarbadhikari, A., Hood, D. R., Gasnault, O., Nambiar, S., & Karunatillake, S. (2022). 2001 Mars Odyssey Gamma Ray Spectrometer Element Concentration Maps. https://doi.org/https://doi.org/10.1029/2022GL099235
            - Data downloaded from https://digitalcommons.lsu.edu/geo_psl/1/
            - Data mirrored to Google Drive for significantly increased downloading speeds

    """

    '''load from pooch download/cache -- turn off the logger so we don't get unnecessary output every time a file is downloaded for the first time'''
    logger = pooch.get_logger()
    logger.disabled = True

    filepaths = pooch.retrieve(
        fname      = '2022_Mars_Odyssey_GRS_Element_Concentration_Maps.zip',
        url        = r'https://drive.google.com/file/d/1Z5Esv-Y4JAQvC84U-VataKJHIJ9OA4_8/view?usp=sharing',
        known_hash = 'sha256:45e047a645ae8d1bbd8e43062adab16a22786786ecb17d8e44bfc95f471ff9b7',
        path       = __datapath,
        downloader = utils.download_gdrive_file,
        processor  = pooch.Unzip(),
    )
    
    logger.disabled = False
    


    for filepath in filepaths:

        filename = os.path.basename(filepath)
        if 'README' in filename: continue

        element_name = filename.split('_')[0].lower()
    

        '''initialize entry in `meta_dat`'''
        __meta_dat[element_name] = {}


        '''import data from files to np.ndarrays'''
        dat = np.loadtxt(filepath, skiprows=1)  
        dat = np.where(dat == 9999.999, get_nanval(), dat)


        """ ==> we hardcode these values because know the data is 5x5 degree grid
        lat_range = utils.unique(dat[:, 0])
        lon_range = utils.unique(dat[:, 1])

        if len(np.unique(np.diff(lon_range).round(decimals=3))) != 1:
            raise Exception('Longitude values are not evenly spaced. This is not supported by the interpolation model.')
        if len(np.unique(np.diff(lat_range).round(decimals=3))) != 1:
            raise Exception('Latitude values are not evenly spaced. This is not supported by the interpolation model.')

        '''edge case (part 1): longitude is cyclical, but data is not, so we duplicate one extra column on each edge of data & lon_range'''
        grid_spacing = np.unique(np.diff(lon_range).round(decimals=3))[0] # grid_spacing based on lon values, so it might be negative if lon is decreasing. but this is okay, it allows the lon cycling to work out.
        meta_dat[element_name]['grid spacing [degrees]'] = abs(grid_spacing)
        lon_range_cycled = np.array([lon_range[0]-grid_spacing, *lon_range, lon_range[-1]+grid_spacing]) # even if grid_spacing is negative, this will work out.
        """


        data_names = ['concentration', 'sigma']

        for i in range(len(data_names)):
            this_data = np.flip(dat[:, 2+i]) # make both latitudes and longitudes increasing
            
            '''reshape to 2D with [lat, lon] indexing'''
            this_data = this_data.reshape(__lat_range.shape[0], __lon_range.shape[0])

            '''units/corrections'''
            if element_name == 'th':
                correction=0.000001 # correct ppm to concentration out of 1
            else:
                correction=0.01 # correct weight percent to concentration out of 1
            this_data = np.where(this_data != get_nanval(), this_data*correction, this_data)


            '''edge case 1: lon is currently [-177.5, 177.5], but we want coverage up to [-180, 180]. Thus we pad each end with WRAPAROUND, leaving some extra space for bilinear interpolation to work.'''
            this_data = np.hstack([this_data[:, -1:], this_data, this_data[:, :1]])

            '''edge case 2: lat is currently [-87.5, 87.5], but we want coverage up to [-90, 90]. Thus we pad each end with DUPLICATION, leaving some extra space for bilinear interpolation to work.'''
            this_data = np.vstack([this_data[:1, :], this_data, this_data[-1:, :]])


            '''add to `meta_dat`'''
            __meta_dat[element_name][data_names[i]] = this_data





    '''use this to pre-compute volatile concentration so we're accessing once instead of thrice. make appropriate changes in `get` as well. note that adding raw data into one grid and then doing bilinear interpolation is not different from doing bilinear interpolation individually and adding them up.'''
    data_names = ['concentration', 'sigma']
    __meta_dat['cl+h2o+s'] = {}

    for data_name in data_names:
        __meta_dat['cl+h2o+s'][data_name] = __meta_dat['cl'][data_name] + __meta_dat['h2o'][data_name] + __meta_dat['s'][data_name]
        __meta_dat['cl+h2o+s'][data_name] = np.where(__meta_dat['cl+h2o+s'][data_name] < 0, get_nanval(), __meta_dat['cl+h2o+s'][data_name])

















############################################################################################################################################
""" functions """




def get(
    element_name: str, 
    lon, lat, 
    normalize = False, 
    quantity = 'concentration'
) -> float:
    """
    DESCRIPTION:
    ------------
        Get GRS-derived concentration/sigma of an element at a desired coordinate.
    
        
    PARAMETERS:
    ------------
        element_name : str
            Element for which you want to make a global concentration map. Options are ['al','ca','cl','fe','h2o','k','si','s','th']. Casing does not matter.
        
        lon : float
            Longitude in range [-180, 180] (lon=0 cuts through Arabia Terra).
        
        lat : float
            Latitude in range [-87.5, 87.5].
        
        normalize : bool (default False)
            If True, normalize to a volatile-free (Cl, H2O, S) basis.
                > "For such measurement [from GRS] to represent the bulk chemistry of the martian upper crust, it must be normalized to a volatile-free basis (22). That equates to a 7 to 14% increase in the K, Th, and U abundances (22), which we applied to the chemical maps by renormalizing to Cl, stoichiometric H2O, and S-free basis."
                Source: "Groundwater production from geothermal heating on early Mars and implication for early martian habitability", Ojha et al. 2020, https://www.science.org/doi/10.1126/sciadv.abb1669
        
        quantity : str (default 'concentration')
            Quantity to plot. Options are ['concentration', 'sigma'].

            
    RETURN:
    ------------
        float
            Surface concentration of an element at the desired coordinate, using bilinear interpolation if that coordinate is not precisely defined by the data
                - Units are in concentration out of one (i.e. original wt% * 0.01 or ppm * 0.000001)
                - If a nearby "pixel" (original 5x5 bin) is unresolved by GRS, just return the nanval.

                
    NOTES:
    ------------
        Our approaches to this computation have been, in order: sloppy manual calculation -> scipy.interpolate.RegularGridInterpolator -> optimized manual calculation (current). Relative to the current approach, the first approach is 2-3x slower (expected due to obvious optimizations), and the second approach is ~10x slower (unexpected, this seems to be a known bug with scipy). See more discussion here: https://stackoverflow.com/questions/75427538/regulargridinterpolator-excruciatingly-slower-than-interp2d/76566214#76566214.

    """

    utils.checkCoords(lon, lat)

    if element_name not in ['al','ca','cl','fe','h2o','k','si','s','th','cl+h2o+s']:
        raise ValueError(f'Element {element_name} is not in list of supported elements: ["al","ca","cl","fe","h2o","k","si","s","th"].')



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
    


    # if element_name in __volatiles:
    #     normalize = False
    #     # The function header defaults `normalize=True`, so a well-meaning user calling `GRS.visualize('h2o')` will encounter the exception 'Cannot normalize a volatile...'. T


    
    if not normalize: # just return the bilinear interpolation on the raw data

        '''get longitude and latitude (`np.searchsorted` returns the index at which the point would be inserted, i.e. point to the 'right', which is why we subtract 1 to get the point to the 'left'. earlier, we padded the edges of the data with extra points to allow for wraparound on the right side, so we don't need to worry about edge cases.)'''
        i_lat = np.searchsorted(__lat_range_ext, lat, side='right') - 1
        j_lon = np.searchsorted(__lon_range_ext, lon, side='right') - 1


        element_name = element_name.lower()


        points = (
            (
                __lon_range_ext                    [j_lon],
                __lat_range_ext                    [i_lat],
                __meta_dat[element_name][quantity] [i_lat, j_lon]
            ),
            (
                __lon_range_ext                    [j_lon+1],
                __lat_range_ext                    [i_lat],
                __meta_dat[element_name][quantity] [i_lat, j_lon+1]
            ),
            (
                __lon_range_ext                    [j_lon],
                __lat_range_ext                    [i_lat+1],
                __meta_dat[element_name][quantity] [i_lat+1, j_lon]
            ),
            (
                __lon_range_ext                    [j_lon+1],
                __lat_range_ext                    [i_lat+1],
                __meta_dat[element_name][quantity] [i_lat+1, j_lon+1]
            ),
        )



        val = bilinear_interpolation(lon, lat, points)

        return val if val >= 0 else get_nanval() # This line ensures that where GRS data is undefined, we return exactly the nanval. Without this, we might return very large negative values that approach the nanval. We mask negative values regardless, but this is more exact. Examples here: https://files.catbox.moe/khetcp.png & https://files.catbox.moe/sri8m4.png
    
    
    else: # Uses recursion. See docstring for more details on `normalize=True` parameter.
        
        __volatiles = ('cl', 'h2o', 's')
        
        if element_name in __volatiles:
            raise Exception('Cannot normalize a volatile (Cl, H2O, or S) to a volatile-free basis.')
        
        raw_concentration = get(element_name=element_name, lon=lon, lat=lat, normalize=False, quantity=quantity)
        if raw_concentration < 0:
            return get_nanval()
        

        '''option 1/2: compute sum of volatiles by accessing/summing each volatile individually'''
        # sum_volatile_concentration = 0
        # for volatile in __volatiles:
        #     volatile_concentration = get(element_name=volatile, lon=lon, lat=lat, normalize=False, quantity=quantity)
        #     if volatile_concentration < 0:
        #         return get_nanval()
        #     sum_volatile_concentration += volatile_concentration
        # return raw_concentration/(1-sum_volatile_concentration)
    

        '''option 2/2: compute sum of volatiles by accessing pre-computed sum of volatiles, noticeably faster. pre-computing is done in section "initialize (run upon import)". '''
        sum_volatile_concentration = get(element_name='cl+h2o+s', lon=lon, lat=lat, normalize=False, quantity=quantity)
        val = raw_concentration/(1-sum_volatile_concentration)
        return val if val >= 0 else get_nanval()

    

















def visualize(
    element_name: str, 
    normalize = False, 
    quantity = 'concentration', 
    lon_bounds = (-177.5,177.5), 
    lat_bounds = (-57.5,57.5), 
    grid_spacing = 5,
    overlay = ...,
    mask_lower = 0,
    mask_upper = ...,
    mask_range = ...,
    title = ...,
    cbar_title = ...,
    colormap = 'viridis',
    transparency_data = ...,
    transparency_mola = ...,
    figsize = ...,
):
    """
    DESCRIPTION:
    ------------
        Create a map of concentration/sigma for some element.
    

    PARAMETERS:
    ------------
        [Star (*) indicates parameters that are not mandatory, but there's a high likelihood users will want to adjust them.]

        For these parameters, see documentation for `redplanet.GRS.get()` or call `help(redplanet.GRS.get)`.
            element_name
            *normalize
            *quantity
    
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
        The default arguments for `lon_bounds`, `lat_bounds`, and `grid_spacing` will display the original 5x5 bins from the data.

    """


    '''kwargs will hold all arguments passed to `redplanet.utils.visualize()`'''
    kwargs = {}



    '''plotThis is the only mandatory argument for `redplanet.utils.visualize()`'''
    def plotThis(lon, lat):
        return get(element_name=element_name, lon=lon, lat=lat, normalize=normalize, quantity=quantity)
    
    

    '''default values that can't be defined in function header'''


    def chem_cased(s1: str) -> str:
        """Convert a string to chemist's casing."""
        s2 = [c.upper() if i == 0 or not s1[i-1].isalpha() else c for i, c in enumerate(s1)]
        return ''.join(s2)
    
    title1 = f'{chem_cased(element_name)} Map from GRS'
    title2 = '(Normalized to Volatile-Free Basis)' if normalize else '(Raw Surface Concentration)'
    title = f'{title1}\n{title2}' if title is ... else title

    cbar_title = f'{quantity.capitalize()} [out of 1]' if cbar_title is ... else cbar_title 



    '''Add all arguments that are either specified by the user or have default values'''
    for key, value in locals().items():
        if value is not ...:
            kwargs[key] = value


    utils.visualize(**kwargs)

    





############################################################################################################################################
__init()