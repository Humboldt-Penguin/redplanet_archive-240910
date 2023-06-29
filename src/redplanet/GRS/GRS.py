"""
Written by Zain Kamal (zain.eris.kamal@rutgers.edu). Last updated 06/28/2023.
https://github.com/Humboldt-Penguin/redplanet

...

RedPlanet module `GRS.py` allows you to get surface element concentrations derived from the 2001 Mar Odyssey Gamma Ray Spectrometer. The original data is defined in 5 degree bins, but this module allows you to calculate values at exact coordinates by linearly interpolating between the four nearest points. Both exact concentration and volatile-free (normalized to an H20/Cl/Si free basis) are available.

...

RESOURCES:
    - Raw data:
        - Paper: https://doi.org/10.1029/2022GL099235
        - Dataset: https://digitalcommons.lsu.edu/geo_psl/1/
    - Processing raw data to `GRS_meta_dat.pkl` file:
        - Option 1: See `redplanet/docs/notebooks/generate_data/GRS/generate_GRS_data.ipynb`
        - Option 2: Run `redplanet tutorial` in command line, navigate to the TODO
    

"""




############################################################################################################################################

from redplanet.DataManager import get_data_path
from redplanet import utils

import numpy as np
import matplotlib.pyplot as plt

import os
import inspect


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








__meta_dat: dict
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


def loadData(path__dataDir: str = None) -> None:
    '''
    Load data from pickled data file. Default option is the data file included in the package, but users can use data they've produced with the `generate_GRS_data.ipynb` notebook. Type `redplanet tutorial` in command line for more details.
    '''
    
    if path__dataDir is None:
        path__thisDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        path__dataDir = utils.getPath(path__thisDir, 'data')

    global __meta_dat
    __meta_dat = {}
    for file in os.listdir(path__dataDir):
        element_name = file[:file.index('_')].lower()
        quantity_name = file[file.index('_')+1:file.index('.')]
        if element_name not in __meta_dat.keys():
            __meta_dat[element_name] = {}
        __meta_dat[element_name][quantity_name] = np.load(utils.getPath(path__dataDir, file))




loadData()





############################################################################################################################################
""" functions """




def __checkCoords(lon: float, lat: float) -> None:
    if not (-180 <= lon <= 180):
        raise ValueError(f'Longitude {lon} is not in range [-180, 180].')
    if not(-87.5 <= lat <= 87.5):
        raise ValueError(f'Latitude {lat} is not in range [-87.5, 87.5].')




def getConcentration(element_name: str, lon: float, lat: float, normalize: bool = True, quantity: str = 'concentration') -> float:
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
        normalize : bool (default True)
            If True, normalize to a volatile-free (Cl, H2O, S) basis.
                > "For such measurement [from GRS] to represent the bulk chemistry of the martian upper crust, it must be normalized to a volatile-free basis (22). That equates to a 7 to 14% increase in the K, Th, and U abundances (22), which we applied to the chemical maps by renormalizing to Cl, stoichiometric H2O, and S-free basis."
                Source: "Groundwater production from geothermal heating on early Mars and implication for early martian habitability", Ojha et al. 2020, https://www.science.org/doi/10.1126/sciadv.abb1669                    

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

        volatiles = ["cl", "h2o", "s"]
        if element_name in volatiles:
            raise Exception('Cannot normalize a volatile to a volatile-free basis.')
        
        raw_concentration = getConcentration(element_name=element_name, lon=lon, lat=lat, normalize=False, quantity=quantity)
        
        sum_volatile_concentration = 0
        for volatile in volatiles:
            volatile_concentration = getConcentration(element_name=volatile, lon=lon, lat=lat, normalize=False, quantity=quantity)
            if volatile_concentration < 0:
                return get_nanval()
            sum_volatile_concentration += volatile_concentration

        return raw_concentration/(1-sum_volatile_concentration)
    







def visualize(element_name: str, normalize: bool = True, quantity: str = 'concentration', lon_left: float = -180, lon_right: float = 180, lat_bottom: float = -75, lat_top: float = 75, grid_spacing: float = 5) -> None:
    """
    DESCRIPTION:
    ------------
        Make a plot of the surface concentration of an element.
    
    PARAMETERS:
    ------------
        element_name : str
            Element for which you want to make a global concentration map. Options are ['al','ca','cl','fe','h2o','k','si','s','th']. Casing does not matter.
        normalize : bool (default True)
            If True, normalize to a volatile-free (Cl, H2O, S) basis. See `getConcentration` docstring for more details.
        quantity : str (default 'concentration')
            Quantity to plot. Options are ['concentration', 'sigma'].
        lon_left, lon_right, lat_bottom, lat_top : float
            Bounding box for visualization. Longitude in range [-180, 180], latitude in range [-87.5, 87.5].
        grid_spacing : float
            Spacing between "pixels" in degrees. Note that original data is 5x5 degree bins, so anything smaller than that will be interpolated. Also note that smaller resolutions will take longer to plot.
                
    """

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
    cbar.set_label(f'{chem_cased(element_name)} Concentration [out of 1]', y=0.5)

    plt.show()