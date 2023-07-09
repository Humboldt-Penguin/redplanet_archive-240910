def preload(*args):
    """
    DESCRIPTION:
    ------------
        Download large files in advance (usually done during module intitialization) and save to cache to speed up later loading. More information about each file downloaded found in respecting module, this is just a shortcut.
    
    PARAMETERS:
    ------------
        args : list[str]
            Choose options from ['GRS', 'Crust']. If empty, default to all.

    """

    if len(args) == 0:
        args = ['GRS', 'Crust']


    from redplanet import utils
    import pooch

    # logger = pooch.get_logger()
    # logger.disabled = True




    ############################################################################################################################################

    if 'GRS' in args:

        datapath = utils.getPath(pooch.os_cache('redplanet'), 'GRS')

        filepaths = pooch.retrieve(
            fname='2022_Mars_Odyssey_GRS_Element_Concentration_Maps.zip',
            url=r'https://drive.google.com/file/d/1Z5Esv-Y4JAQvC84U-VataKJHIJ9OA4_8/view?usp=sharing',
            known_hash='sha256:45e047a645ae8d1bbd8e43062adab16a22786786ecb17d8e44bfc95f471ff9b7',
            path=datapath,
            downloader=utils.download_gdrive_file,
            processor=pooch.Unzip(),
        )


        filepath = pooch.retrieve(
            fname='Mars_HRSC_MOLA_BlendShade_Global_200mp_v2_resized-7.tif',
            url=r'https://drive.google.com/file/d/1i278DaeaFCtY19vREbE35OIm4aFRKXiB/view?usp=sharing',
            known_hash='sha256:93d32f9b404b7eda1bb8b05caa989e55b219ac19a005d720800ecfe6e2b0bb6c',
            path=utils.getPath(pooch.os_cache('redplanet'), 'Maps'),
            downloader=utils.download_gdrive_file
        )
            
            



    ############################################################################################################################################

    if 'Crust' in args:

        datapath = utils.getPath(pooch.os_cache('redplanet'), 'Crust')

        # high res topography model (sh coeff 2600)
        filepath = pooch.retrieve(
            fname='MarsTopo2600.shape.gz',
            url=r'https://drive.google.com/file/d/1so3sGXNzdYkTdpzjvOxwYBsvr1Y1lwXt/view?usp=sharing',
            known_hash='sha256:8882a9ee7ee405d971b752028409f69bd934ba5411f1c64eaacd149e3b8642af',
            path=datapath,
            downloader=utils.download_gdrive_file,
        )

        # raw data (moho sh coeffs) registry    
        filepath = pooch.retrieve(
            fname='Crust_mohoSHcoeffs_rawdata_registry.json',
            url=r'https://drive.google.com/file/d/17JJuTFKkHh651-rt2J2eFKnxiki0w4ue/view?usp=sharing',
            known_hash='sha256:1800ee2883dc6bcc82bd34eb2eebced5b59fbe6c593cbc4e9122271fd01c1491',
            path=datapath, 
            downloader=utils.download_gdrive_file,
        )

        # dichotomy coordinates
        filepath = pooch.retrieve(
            fname='dichotomy_coordinates-JAH-0-360.txt',
            url=r'https://drive.google.com/file/d/17exPNRMKXGwa3daTEBN02llfdya6OZJY/view?usp=sharing',
            known_hash='sha256:42f2b9f32c9e9100ef4a9977171a54654c3bf25602555945405a93ca45ac6bb2',
            path=datapath,
            downloader=utils.download_gdrive_file,
        )



        filepath = pooch.retrieve(
            fname='Mars_HRSC_MOLA_BlendShade_Global_200mp_v2_resized-7.tif',
            url=r'https://drive.google.com/file/d/1i278DaeaFCtY19vREbE35OIm4aFRKXiB/view?usp=sharing',
            known_hash='sha256:93d32f9b404b7eda1bb8b05caa989e55b219ac19a005d720800ecfe6e2b0bb6c',
            path=utils.getPath(pooch.os_cache('redplanet'), 'Maps'),
            downloader=utils.download_gdrive_file
        )


    ############################################################################################################################################

    # logger.disabled = False








def clear_cache(force=False):
    """
    DESCRIPTION:
    ------------
        Clear the cache folder of all files downloaded by redplanet.

    """

    import pooch
    import os
    import shutil

    datapath = pooch.os_cache('redplanet')

    if os.path.exists(datapath):
        print(f'Are you sure you want to delete all files in {datapath}? (y/n) ')
        if force or input() == 'y':
            print('Deleting files...')
            shutil.rmtree(datapath)
            print('Done.')