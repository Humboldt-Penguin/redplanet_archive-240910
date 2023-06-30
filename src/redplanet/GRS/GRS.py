"""
Written by Zain Kamal (zain.eris.kamal@rutgers.edu). Last updated 06/28/2023.
https://github.com/Humboldt-Penguin/redplanet

For more information, call `help(GRS)` or directly view docstring in `GRS/__init__.py`.

"""



############################################################################################################################################

# from redplanet import utils

import pooch
import numpy as np
import matplotlib.pyplot as plt

# import os
# import inspect




############################################################################################################################################
""" module variables """

__nanval: float = -1e10
'''
Value given to pixels where data is not defined (i.e. "NOT_APPLICABLE_CONSTANT"). In the data, this is 9999.999.
We choose an extremely large negative value so we can easily filter/mask it when using the data or plotting. This errs on the side of caution.
'''

def get_nanval() -> float:
    return __nanval








grid_spacing = 5 # degrees
lat_range = np.arange(87.5, -87.5 *1.0001, -grid_spacing)
lon_range = np.arange(177.5, -177.5 *1.0001, -grid_spacing)
lon_range_cycled = np.arange(182.5, -182.5 *1.0001, -grid_spacing)
'''
We opt to hardcode these values in the case of GRS because it's static. It's not hard to programmatically calculate these values in other cases -- the code for such is included but commented out below.
'''






rawdata_registry = {
    'al': {
        'hash': 'sha256:a5bc7cd78d8dcf9caa42b69a044b70d0d65bfff73c321bad6d501faa2d80fd64',
        'link': 'https://digitalcommons.lsu.edu/cgi/viewcontent.cgi?filename=9&article=1000&context=geo_psl&type=additional',
    },
    'ca': {
        'hash': 'sha256:b8b94cee7bd66a9592c1b22d4a454848f884e38c9df211ebaebbd657784de2bb',
        'link': 'https://digitalcommons.lsu.edu/cgi/viewcontent.cgi?filename=10&article=1000&context=geo_psl&type=additional',
    },
    'cl': {
        'hash': 'sha256:c1d09c28c43a2881cdf586a5256dcf6717939d384426307801145b2a8a104dcd',
        'link': 'https://digitalcommons.lsu.edu/cgi/viewcontent.cgi?filename=11&article=1000&context=geo_psl&type=additional',
    },
    'fe': {
        'hash': 'sha256:735ffe97802e75eadaa1e82f2bcd836d1d2a6974dbac16ec83b242ec98b3033f',
        'link': 'https://digitalcommons.lsu.edu/cgi/viewcontent.cgi?filename=12&article=1000&context=geo_psl&type=additional',
    },
    'h2o': {
        'hash': 'sha256:2af6271b0718049c861531346e976feeab93ad487b15ad5eff5e268128d2167c',
        'link': 'https://digitalcommons.lsu.edu/cgi/viewcontent.cgi?filename=13&article=1000&context=geo_psl&type=additional',
    },
    'k': {
        'hash': 'sha256:0b03d23761a4ad490b5d1082389e8aaacdd5c904fef5e0d5031a9d9c2c2a63d6',
        'link': 'https://digitalcommons.lsu.edu/cgi/viewcontent.cgi?filename=14&article=1000&context=geo_psl&type=additional',
    },
    'si': {
        'hash': 'sha256:65069e80bd80fddca89eade1b9c514348eebbf768e6d789e2ea932ec642a1575',
        'link': 'https://digitalcommons.lsu.edu/cgi/viewcontent.cgi?filename=16&article=1000&context=geo_psl&type=additional',
    },
    's': {
        'hash': 'sha256:6f70b4aa6f2eee604aec45f40eb5ccb21c2e320bc4830bdc7060205e769beaff',
        'link': 'https://digitalcommons.lsu.edu/cgi/viewcontent.cgi?filename=15&article=1000&context=geo_psl&type=additional',
    },
    'th': {
        'hash': 'sha256:37289ccd5b6819b2fba6b53d4604cc17875ffe73cbc60fd965e65af1747fdd65',
        'link': 'https://digitalcommons.lsu.edu/cgi/viewcontent.cgi?filename=17&article=1000&context=geo_psl&type=additional',
    },
}

'''
We download data directly from the source (more information on the source `__init__.py` docstring). 

Downloads are executed through the `pooch` package, which ensures that the data is downloaded only once and then cached locally. This requires both the download link and hash of the file (to verify integrity / alert to modifications), which are pre-computed and stored in `rawdata_registry`. 

A convenient script to generate this dictionary:
    import os
    rawdata_registry = {}
    names = ['Al','Ca','Cl','Fe','H2O','K','S','Si','Th']
    folder = r'C:/Users/Eris/Downloads/redplanet-data/GRS/1_raw'
    for file in os.listdir(folder):
        if 'README' in file: continue
        element_name = file[:file.index('_')]
        hash = pooch.file_hash(fname=os.path.join(folder, file), alg='sha256')
        hash = f'sha256:{hash}'
        i = names.index(element_name) + 9
        link = f'https://digitalcommons.lsu.edu/cgi/viewcontent.cgi?filename={i}&article=1000&context=geo_psl&type=additional'
        rawdata_registry[element_name.lower()] = {'hash': hash, 'link': link}
    from redplanet import utils
    utils.print_dict(rawdata_registry, format_pastable=True)

'''





__volatiles = ('cl', 'h2o', 's')
'''
Volatile elements. Used in `getConcentration` to normalize to a volatile-free basis. See docstring for more details.
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

for element_name in rawdata_registry:

    '''load from pooch download/cache'''
    filepath = pooch.retrieve(
        url=rawdata_registry[element_name]['link'],
        known_hash=rawdata_registry[element_name]['hash'],
        path=pooch.os_cache('redplanet')
    )

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

    '''edge case (part 1/2): longitude is cyclical, but data is not, so we duplicate one extra column on each edge of data & lon_range'''
    grid_spacing = np.unique(np.diff(lon_range).round(decimals=3))[0] # grid_spacing based on lon values, so it might be negative if lon is decreasing. but this is okay, it allows the lon cycling to work out.
    meta_dat[element_name]['grid spacing [degrees]'] = abs(grid_spacing)
    lon_range_cycled = np.array([lon_range[0]-grid_spacing, *lon_range, lon_range[-1]+grid_spacing]) # even if grid_spacing is negative, this will work out.
    """


    data_names = ['concentration', 'sigma']

    for i in range(len(data_names)):
        this_data = dat[:, 2+i]
        
        '''reshape to 2D, transpose to get [lon,lat] indexing'''
        this_data = this_data.reshape(lat_range.shape[0], lon_range.shape[0]).T
        # for index (i,j), `i` is longitude from `lon_range[0]` to `lon_range[-1]`, `j` is latitude from `lat_range[0]` to `lat_range[-1]`


        '''units/corrections'''
        if element_name == 'th':
            correction=0.000001 # correct ppm to concentration out of 1
        else:
            correction=0.01 # correct weight percent to concentration out of 1
        this_data = np.where(this_data != get_nanval(), this_data*correction, this_data)


        '''edge case (part 2/2): longitude is cyclical, but data is not, so we duplicate one extra column on each edge of data & lon_range'''
        left_edge = this_data[0, :]
        right_edge = this_data[-1, :]
        this_data = np.array([right_edge, *this_data, left_edge])


        '''add to `meta_dat`'''
        __meta_dat[element_name][data_names[i]] = this_data























############################################################################################################################################
""" functions """




def __checkCoords(lon: float, lat: float) -> None:
    if not (-180 <= lon <= 180):
        raise ValueError(f'Longitude {lon} is not in range [-180, 180].')
    if not(-87.5 <= lat <= 87.5):
        raise ValueError(f'Latitude {lat} is not in range [-87.5, 87.5].')




def getConcentration(element_name: str, lon: float, lat: float, normalize=False, quantity='concentration') -> float:
    """
    DESCRIPTION:
    ------------
        Get the concentration of an element at the desired coordinate derived from GRS data.
    
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

    __checkCoords(lon, lat)



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

        # since `lon_range_cycled` and `lat_range` are decreasing rather than increasing, we do some trickery on top of `np.searchsorted()` to get the desired indices.
        i_lon = lon_range_cycled.shape[0] - np.searchsorted(np.flip(lon_range_cycled), lon)
        j_lat = lat_range.shape[0] - np.searchsorted(np.flip(lat_range), lat)

        element_name = element_name.lower()

        points = (
            (
                lon_range_cycled[i_lon - 1],
                lat_range[j_lat - 1],
                __meta_dat[element_name][quantity][i_lon - 1, j_lat - 1]
            ),
            (
                lon_range_cycled[i_lon],
                lat_range[j_lat - 1],
                __meta_dat[element_name][quantity][i_lon, j_lat - 1]
            ),
            (
                lon_range_cycled[i_lon - 1],
                lat_range[j_lat],
                __meta_dat[element_name][quantity][i_lon - 1, j_lat]
            ),
            (
                lon_range_cycled[i_lon],
                lat_range[j_lat],
                __meta_dat[element_name][quantity][i_lon, j_lat]
            )
        )


        # ### alternative version to the above that uses list comprehension as opposed to hard-coding -- functionally equivalent, possibly faster. i don't know.
        # points = [
        #     (
        #         lon_range_cycled[i_lon-1+i],
        #         lat_range[j_lat-1+j],
        #         meta_dat[element_name][quantity][i_lon-1+i, j_lat-1+j]
        #     )
        #     for i, j in [(i, j) for i in range(2) for j in range(2)]
        # ]
        

        return bilinear_interpolation(lon, lat, points)
    
    
    else: # Uses recursion. See docstring for more details on `normalize=True` parameter.

        if element_name in __volatiles:
            raise Exception('Cannot normalize a volatile to a volatile-free basis.')
        
        raw_concentration = getConcentration(element_name=element_name, lon=lon, lat=lat, normalize=False, quantity=quantity)
        
        sum_volatile_concentration = 0
        for volatile in __volatiles:
            volatile_concentration = getConcentration(element_name=volatile, lon=lon, lat=lat, normalize=False, quantity=quantity)
            if volatile_concentration < 0:
                return get_nanval()
            sum_volatile_concentration += volatile_concentration

        return raw_concentration/(1-sum_volatile_concentration)
    







def visualize(element_name: str, normalize=False, quantity='concentration', 
              lon_bounds: tuple = (-180,180), #lon_left: float = -180, lon_right: float = 180, 
              lat_bounds: tuple = (-75,75), #lat_bottom: float = -75, lat_top: float = 75, 
              grid_spacing: float = 5) -> None:
    """
    DESCRIPTION:
    ------------
        Make a plot of the surface concentration of an element.
    
    PARAMETERS:
    ------------
        element_name : str
            Element for which you want to make a global concentration map. Options are ['al','ca','cl','fe','h2o','k','si','s','th']. Casing does not matter.
        normalize : bool (default False)
            If True, normalize to a volatile-free (Cl, H2O, S) basis. See `getConcentration` docstring for more details.
        quantity : str (default 'concentration')
            Quantity to plot. Options are ['concentration', 'sigma'].
        lon_bounds, lat_bounds : tuple(2 floats) (default entire map)
            Bounding box for visualization. Longitude in range [-180, 180], latitude in range [-87.5, 87.5].
        grid_spacing : float (default 5 degrees)
            Spacing between "pixels" in degrees. Note that original data is 5x5 degree bins, so anything smaller than that will be interpolated. Also note that smaller resolutions will take longer to plot.
                
    """

    lon_left, lon_right = lon_bounds
    lat_bottom, lat_top = lat_bounds

    __checkCoords(lon_left, lat_bottom)
    __checkCoords(lon_left, lat_top)
    __checkCoords(lon_right, lat_bottom)
    __checkCoords(lon_right, lat_top)

    # import time
    # iterations = 10
    # t0 = time.time()
    # for i in range(iterations):

    ### If adapting visualization function, modify this function
    def plotThis(lon, lat):
        val = getConcentration(element_name=element_name, lon=lon, lat=lat, normalize=normalize, quantity=quantity)
        return val


    dat = [[
        plotThis(lon,lat)
        for lon in np.arange(lon_left, lon_right, grid_spacing)]
        for lat in np.arange(lat_bottom, lat_top, grid_spacing)]

    # t1 = time.time()
    # total1 = (t1-t0)/iterations
    # print(f'Time elapsed: {total1} seconds.')
    # print(f'speed changed by factor of {total2/total1}')

    '''apply mask'''
    dat = np.asarray(dat)
    dat = np.ma.masked_where((dat < 0), dat)

    '''primary plot'''
    fig = plt.figure(figsize=(10,7))
    ax = plt.axes()
    im = ax.imshow(dat[::-1], cmap='jet', extent=[lon_left, lon_right, lat_bottom, lat_top])




    def chem_cased(s1: str) -> str:
        """Convert a string to chemist's casing."""
        # s2 = ''
        # for i, c in enumerate(s1):
        #     if i == 0 or not(s1[i-1].isalpha()):
        #         s2 += c.upper()
        #     else:
        #         s2 += c
        # return s2
        s2 = [c.upper() if i == 0 or not s1[i-1].isalpha() else c for i, c in enumerate(s1)]
        return ''.join(s2)



    '''titles'''
    ax.set_title(f'{"Normalized" if normalize else "Raw"} {chem_cased(element_name)} Map from GRS')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    '''axis formatter'''
    ax.xaxis.set_major_formatter('{x}$\degree$')
    ax.yaxis.set_major_formatter('{x}$\degree$')


    # (aesthetic preference)
    if lon_bounds == (-180,180):
        x_spacing = 60
        ax.set_xticks(np.linspace(lon_left, lon_right, int((lon_right-lon_left)/x_spacing)+1))


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
    cbar.set_label(f'{chem_cased(element_name)} {quantity.capitalize()} [out of 1]', y=0.5)

    plt.show()