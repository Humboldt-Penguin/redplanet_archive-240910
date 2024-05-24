"""
RedPlanet is a Python package that gives an easy way to work with various Mars datasets. With straightforward methods and high customizability, you can either create publication-ready plots on the fly, or access the underlying data for more involved calculations.

- Project repository: https://github.com/Humboldt-Penguin/redplanet
- Interactive, web-based tutorial on Google Colab: https://drive.google.com/drive/folders/1UxBJzFugjNnjnxebbso7bYJ1cYgEZyzj?usp=sharing


###################################################################################
------------
MODULES:
------------
- GRS
    - Access and plot surface element concentrations derived from the 2001 Mar Odyssey Gamma Ray Spectrometer.
- Crust
    - Access and plot high-resolution data for topography, moho, crustal thickness, and crustal density derived from spherical harmonics.
- Craters
    - Access coordinates, names, and diameters of Martian craters greater than 10km diameter.


    
###################################################################################
------------
METHODS:
------------

>>> redplanet.preload(*args)

Download large files in advance (usually done during module intitialization) and save to cache to speed up later loading. More information about each file downloaded found in respecting module, this is just a shortcut.



>>> redplanet.clear_cache(force=False)

Clear the cache folder containing all files downloaded by redplanet. Max size will not exceed 1GB. If `force=True`, will not prompt with folder name and ask for confirmation.




###################################################################################
------------
QUICKSTART:
------------

To get started, run:
>>> from redplanet import <module>
>>> help(<module>)


"""



def preload(datasets):
    '''
    TODO: 
        rather than having to create/manage a decentralized `pooch` registry thing (lots of time/effort, AVOID AT ALL COSTS AND FOCUS ON IMPORTANT STUFF), it's much easier to import the modules and do some basic operations that will result in downloading the necessary files!!! MUCH easier.
    '''


    if datasets == 'all':
        datasets = [
            'GRS',
            'Crust',
            'Mag',
            'Craters',
        ]


    if 'GRS' in datasets:
        ...
    if 'Crust' in datasets:
        ...
    if 'Mag' in datasets:
        ...
    if 'Craters' in datasets:
        ...
    

    return




# def clear_cache(force=False):
#     """
#     DESCRIPTION:
#     ------------
#         Clear the cache folder containing all files downloaded by redplanet. Max size will not exceed 1GB. If `force=True`, will not prompt with folder name and ask for confirmation.

#     """

#     import pooch
#     import os
#     import shutil

#     datapath = pooch.os_cache('redplanet')

#     if os.path.exists(datapath):
#         print(f'Are you sure you want to delete all files in {datapath}? (y/n) ')
#         if force or input() == 'y':
#             print('Deleting files...')
#             shutil.rmtree(datapath)
#             print('Done.')




# def cite():
#     """
#     DESCRIPTION:
#     ------------
#         Print out citation information for redplanet.

#     """

#     print('Thank you for using redplanet! If you use this in your research, please cite:')
#     print()
#     print('Citation information coming soon!')
#     # print()
#     # print('Bibtex:')

