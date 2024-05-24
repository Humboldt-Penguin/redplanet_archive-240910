"""
Written by Zain Kamal (zain.eris.kamal@rutgers.edu).
https://github.com/Humboldt-Penguin/redplanet

For more information, call `help(Heat)` or directly view docstring in `Heat/__init__.py`.

"""



############################################################################################################################################

from redplanet import utils

from redplanet import Crust
from redplanet import GRS

import numpy as np




############################################################################################################################################
""" module variables """





############################################################################################################################################
""" functions """


from redplanet.Crust import load_model as load_crust_model









def calc_H(
    lon: float, 
    lat: float, 
    t_Ga: float, 
    normalize=True
) -> float:
    """
    DESCRIPTION:
    ------------
        Calculate heat production rate in lithosphere [W/kg] at a specific coordinate/time due to decay of radiogenic heat producing elements (U238, U235, Th232, K40).

    
    PARAMETERS:
    ------------
        lon, lat : float
            Coordinates in degrees, with longitude in range [-180, 180] and latitude in range [-90, 90]. (This is used to get GRS data.)

        t_Ga : float
            How many billions of years in the past to calculate H. (This is used to calculate elapsed half-lives of radiogenic HPEs.)

        normalize : bool (default True)
            If True, normalize to a volatile-free (Cl, H2O, S) basis to get a value representative of the bulk crust chemistry. See `GRS.get()` documentation for more information. We do not recommend turning this off.

            
    RETURN:
    ------------
        float
            Heat production rate in lithosphere [W/kg] at a specific coordinate/time due to decay of radiogenic heat producing elements (U238, U235, Th232, K40).

            
    REFERENCES:
    ------------
        Method to calculate heat production rate from radiogenic heat producing elements (HPEs) are based on the following:
            > Hahn, B. C., McLennan, S. M., and Klein, E. C. (2011), Martian surface heat production and crustal heat flow from Mars Odyssey Gamma-Ray spectrometry, Geophys. Res. Lett., 38, L14203, doi:10.1029/2011GL047435.
            > Turcotte, D. L., and G. Schubert (2001), Geodynamics, 2nd ed., Cambridge Univ. Press, Cambridge, U. K. (chapter 4).

    """

    utils.checkCoords(lon, lat)


    '''initialize heat producing element constants'''
    HPE = {
        'U238': {
            'isotopic_frac': 0.9928, # natural abundance of this isotope relative to all isotopes of this element
            'heat_release_const': 9.46e-5, # net energy per unit mass [W/kg]
            'half_life': 4.47e9 # half life [yr]
        },
        'U235': {
            'isotopic_frac': 0.0071,
            'heat_release_const': 5.69e-4,
            'half_life': 7.04e8
        },
        'Th232': {
            'isotopic_frac': 1.00,
            'heat_release_const': 2.64e-5,
            'half_life': 1.40e10
        },
        'K40': {
            'isotopic_frac': 1.191e-4,
            'heat_release_const': 2.92e-5,
            'half_life': 1.25e9
        }
    }


    '''concentrations'''
    HPE['Th232']['concentration'] = GRS.get(element_name='th', lon=lon, lat=lat, normalize=normalize, quantity='concentration')
    HPE['K40']['concentration'] = GRS.get(element_name='k', lon=lon, lat=lat, normalize=normalize, quantity='concentration')

    HPE['U235']['concentration'] = HPE['U238']['concentration'] = HPE['Th232']['concentration'] / 3.8

    for element in HPE:
        # if HPE[hpe]['concentration'] == GRS.get_nanval:
        if HPE[element]['concentration'] < 0:
            return GRS.get_nanval()
        
        
    '''calculate crustal heat production'''
    t_yr = t_Ga * 1e9
    H = 0
    for element in HPE:
        H += (
            HPE[element]['isotopic_frac'] *
            HPE[element]['concentration'] *
            HPE[element]['heat_release_const'] *
            np.exp( (t_yr * np.log(2)) / HPE[element]['half_life'] )
        )

    return H
















def calc_temp_at_depth(
    lon: float,
    lat: float,
    depth_km: float,
    t_Ga: float,
    q_b_mW = 0,
    k_cr = 2.5,
    k_m = 4,
) -> float:
    """
    DESCRIPTION:
    ------------
        Calculate ambient temperature at some depth.

    
    PARAMETERS:
    ------------
        lon, lat : float
            Coordinates in degrees, with longitude in range [-180, 180] and latitude in range [-90, 90]. 

        depth_km : float
            Calculate the temperature at this depth [km].

        t_Ga : float
            How many billions of years in the past to calculate H. (This is used to calculate elapsed half-lives of radiogenic HPEs.) 

        q_b_mW : float (default 0)
            Basal heat flow [mW/m^2].

        k_cr : float (default 2.5)
            Thermal conductivity of crust [W m^-1 K^-1].
        
        k_m : float (default 4)
            Thermal conductivity of mantle [W m^-1 K^-1].

            
    RETURN:
    ------------
        float
            Temperature in Celsius.

            
    REFERENCES:
    ------------
        Equation to calculate calculate temperature:
            > Ojha, L., Karimi, S., Lewis, K. W., Smrekar, S. E., & Siegler, M. (2019). Depletion of Heat Producing Elements in the Martian Mantle. Geophysical Research Letters, 46, 12756– 12763. https://doi.org/10.1029/2019GL085234
                - Specifically, see supplemental text 3. We use this equation.
            > Turcotte, D. L., and G. Schubert (2001), Geodynamics, 2nd ed., Cambridge Univ. Press, Cambridge, U. K. (chapter 4).
                - The equation is slightly differently, namely not piecewise to account for depletion of HPEs in the mantle. We do not use this equation, but the information might be helpful. 

    """
    
    H = calc_H(lon, lat, t_Ga, normalize=True)

    if H == GRS.get_nanval():
        return GRS.get_nanval()
    
    depth_m = depth_km * 1.e3
    crthick_m = Crust.get('thick', lon, lat) * 1.e3
    rho = Crust.get('rho', lon, lat)
    q_b = q_b_mW * 1e-3


    def T_eq1(z_m):
        return (
            rho * H * z_m * (crthick_m - z_m/2) / k_cr
            + q_b * z_m / k_cr
        )
    def T_eq2(z):
        return (
            rho * H * crthick_m**2 / (2*k_m)
            + q_b * z / k_m
        )


    if depth_m < crthick_m:
        T = T_eq1(z_m=depth_m)
    else:
        T_0 = T_eq1(z_m=crthick_m) - T_eq2(z=crthick_m) # ensure continutity at crust-mantle boundary
        T = T_0 + T_eq2(z=depth_m)

    return T




















def calc_depth_at_temp(
    lon: float,
    lat: float,
    temp_C: float,
    t_Ga: float,
    q_b_mW = 0,
    k_cr = 2.5,
    k_m = 4,
) -> float:
    """
    DESCRIPTION:
    ------------
        Calculate how deep you need to go to reach some ambient temperature. This is nearly identical to `calc_temp_at_depth()` as we're just (binary) searching the crust for a point where the desired temperature is reached -- we simply optimize it so values aren't unnecessarily recomputed. 

    
    PARAMETERS:
    ------------
        lon, lat : float
            Coordinates in degrees, with longitude in range [-180, 180] and latitude in range [-90, 90]. 

        temp_C : float
            Calculate the depth that is at this temperature [C].

        t_Ga : float
            How many billions of years in the past to calculate H. (This is used to calculate elapsed half-lives of radiogenic HPEs.) 

        q_b_mW : float (default 0)
            Basal heat flow [mW/m^2].

        k_cr : float (default 2.5)
            Thermal conductivity of crust [W m^-1 K^-1].
        
        k_m : float (default 4)
            Thermal conductivity of mantle [W m^-1 K^-1].

            
    RETURN:
    ------------
        float
            Depth in km.

            
    REFERENCES:
    ------------
        Equation to calculate calculate temperature:
            > Ojha, L., Karimi, S., Lewis, K. W., Smrekar, S. E., & Siegler, M. (2019). Depletion of Heat Producing Elements in the Martian Mantle. Geophysical Research Letters, 46, 12756– 12763. https://doi.org/10.1029/2019GL085234
                - Specifically, see supplemental text 3. We use this equation.
            > Turcotte, D. L., and G. Schubert (2001), Geodynamics, 2nd ed., Cambridge Univ. Press, Cambridge, U. K. (chapter 4).
                - The equation is slightly differently, namely not piecewise to account for depletion of HPEs in the mantle. We do not use this equation, but the information might be helpful. 

    """
    
    H = calc_H(lon, lat, t_Ga, normalize=True)

    if H == GRS.get_nanval():
        return GRS.get_nanval()
    
    crthick_m = Crust.get('thick', lon, lat) * 1.e3
    rho = Crust.get('rho', lon, lat)
    q_b = q_b_mW * 1e-3


    def calc_T(depth_km):

        depth_m = depth_km * 1.e3

        def T_eq1(z_m):
            return (
                rho * H * z_m * (crthick_m - z_m/2) / k_cr
                + q_b * z_m / k_cr
            )
        def T_eq2(z):
            return (
                rho * H * crthick_m**2 / (2*k_m)
                + q_b * z / k_m
            )

        if depth_m < crthick_m:
            T = T_eq1(z_m=depth_m)
        else:
            T_0 = T_eq1(z_m=crthick_m) - T_eq2(z=crthick_m) # ensure continutity at crust-mantle boundary
            T = T_0 + T_eq2(z=depth_m)

        return T
    

    '''use binary search to find depth at which T = temp_C, within some error (tweak for desired accuracy)'''

    depth_left_km, depth_right_km = 0, 1000
    depth_mid_km = (depth_left_km + depth_right_km) / 2

    T_left = calc_T(depth_km=depth_left_km)
    T_right = calc_T(depth_km=depth_right_km)
    T_mid = calc_T(depth_km=depth_mid_km)

    if temp_C <= T_left or T_right <= temp_C:
        return GRS.get_nanval()

    error = 1e-2
    while abs(T_mid - temp_C) > error:
            
        if temp_C < T_mid:
            depth_right_km = depth_mid_km
        else:
            depth_left_km = depth_mid_km

        depth_mid_km = (depth_left_km + depth_right_km) / 2
        T_mid = calc_T(depth_km=depth_mid_km)


    return depth_mid_km
    









def visualize(
    quantity: str,
    depth_km = ...,
    temp_C = ...,
    q_b_mW = 0,
    k_cr = 2.5,
    k_m = 4,
    t_Ga = 0,
    lon_bounds = (-180,180), 
    lat_bounds = (-60,60), 
    grid_spacing = 1,
    overlay = ...,
    mask_lower = 0,
    mask_upper = ...,
    mask_range = ...,
    title = ...,
    cbar_title = ...,
    colormap = ...,
    transparency_data = ...,
    transparency_mola = ...,
    figsize = ...,
):
    """
    DESCRIPTION:
    ------------
        Create a map of: 
            - 'H' -- heat production per unit mass in the lithosphere [W/kg],
            - 'heat flow' -- crustal heat flow [mW/m^2],
            - 'temp at depth' -- temperature at a specified depth [C],
            - 'depth at temp' -- depth at which temperature is a specified value [km]. 
        
        If a crustal thickness model is used, the name is formatted f'{Reference_Interior_Model}-{insight_thickness}-{rho_south}-{rho_north}'.
    
        
    PARAMETERS:
    ------------
        quantity : str
            Options are ['H', 'heat flow', 'temp at depth', 'depth at temp'].

            [If 'H':]
                - No additional arguments needed.
            
            [If 'heat flow':]
                - No additional arguments needed.
            
            [If 'temp at depth': (see `calc_temp_at_depth()` documentation for more information)]
                depth_km : float
                    Calculate the temperature at this depth [km].
                q_b_mW : float (default 0)
                    Basal heat flow [mW/m^2].
                k_cr : float (default 2.5)
                    Thermal conductivity of crust [W m^-1 K^-1].
                k_m : float (default 4)
                    Thermal conductivity of mantle [W m^-1 K^-1].
            
            [If 'depth at temp': (see `calc_depth_at_temp()` documentation for more information)]
                temp_C : float
                    Calculate the depth that is at this temperature [C].
                q_b_mW : float (default 0)
                    Basal heat flow [mW/m^2].
                k_cr : float (default 2.5)
                    Thermal conductivity of crust [W m^-1 K^-1].
                k_m : float (default 4)
                    Thermal conductivity of mantle [W m^-1 K^-1].


        t_Ga : float (default 0)
            How many billions of years in the past to calculate H. (This is used to calculate elapsed half-lives of radiogenic HPEs.)



    PARAMETERS:
    ------------
        [Star (*) indicates parameters that are not mandatory, but there's a high likelihood users will want to adjust them.]

        For these parameters, see documentation for: `Heat.calc_H()`, `Heat.calc_temp_at_depth()`, `Heat.calc_depth_at_temp()`.
            ...
    
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

    """


    '''kwargs will hold all arguments passed to `redplanet.utils.visualize()`'''
    kwargs = {}


        

    '''default values that can't be defined in function header'''


    match quantity:
        case 'H':
            def plotThis(lon, lat):
                return calc_H(lon, lat, t_Ga, normalize=True)
            
            title1 = 'Crustal Heat Production'
            title2 = f'($t = {t_Ga}$ Ga)'
            title = f'{title1}\n{title2}' if title is ... else title

            cbar_title = '[W / kg]' if cbar_title is ... else cbar_title
            
            colormap = 'magma' if colormap is ... else colormap


        case 'heat flow':
            def plotThis(lon, lat):
                rho = Crust.get('rho', lon, lat)
                H = calc_H(lon, lat, t_Ga, normalize=True)
                z = Crust.get('thick', lon, lat) * 1.e3
                return rho * H * z * 1.e3

            title1 = 'Crustal Heat Flow'
            title2 = f'($t = {t_Ga}$ Ga, Crust Model: {Crust.get_model_name()})'
            title = f'{title1}\n{title2}' if title is ... else title

            cbar_title = '[mW / m$^2$]' if cbar_title is ... else cbar_title

            colormap = 'inferno' if colormap is ... else colormap


        case 'temp at depth':
            def plotThis(lon, lat):
                return calc_temp_at_depth(lon, lat, depth_km, t_Ga, q_b_mW, k_cr, k_m)
            
            title1 = f'Temperature at Depth = {depth_km} km'
            title2 = f'($t = {t_Ga}$ Ga, $q_b = {q_b_mW}\ mW$, Crust Model: {Crust.get_model_name()})'
            title = f'{title1}\n{title2}' if title is ... else title

            cbar_title = '[$\degree$C]' if cbar_title is ... else cbar_title
            
            colormap = 'plasma' if colormap is ... else colormap


        case 'depth at temp':
            def plotThis(lon, lat):
                return calc_depth_at_temp(lon, lat, temp_C, t_Ga, q_b_mW, k_cr, k_m)

            title1 = f'Depth at which $T={temp_C}\degree C$'
            title2 = f'($t = {t_Ga}$ Ga, Crust Model: {Crust.get_model_name()})'
            title = f'{title1}\n{title2}' if title is ... else title

            cbar_title = '[km]' if cbar_title is ... else cbar_title

            colormap = 'viridis' if colormap is ... else colormap


        case _:
            raise ValueError(f'Quantity {quantity} not recognized. Options are ["H", "heat flow", "temp at depth", "depth at temp"].')
        








    '''Add all arguments that are either specified by the user or have default values'''
    for key, value in locals().items():
        if value is not ...:
            kwargs[key] = value


    utils.visualize(**kwargs)



