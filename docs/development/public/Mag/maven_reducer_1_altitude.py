"""
Written by Zain Kamal (zain.eris.kamal@rutgers.edu).
https://github.com/Humboldt-Penguin/redplanet

------------

This script allows you to reduce the size of the MAVEN magnetometer dataset by filtering out data above a certain altitude. This leads to significant reductions in file sizes and read/processing time (>95% of data point are removed when max altitude is set to 200 km, and file size + read time are further improved by the .npy file type). 


Users must manually download the zipped raw MAVEN data, but it should NOT be unzipped. This removes the onus to unzip data from the user, saving 5x the space and significant time. 
Options to download the zipped data are:
    (1) Downloading yearly data from our Google Drive mirror (~20 GB each), which has significantly faster download speeds: https://drive.google.com/drive/folders/1iRJoprOsjB02DYjtk8wr8LExupcdWY5y
    (2) Download either full, yearly, or monthly data from NASA PDS, which is much slower and prone to timeouts: https://pds-ppi.igpp.ucla.edu/search/view/?f=null&id=pds://PPI/maven.mag.calibrated/data/pc/highres
See section "user inputs" for more information.


Again, the raw data should NOT be unzipped -- this script only takes zip folders as input, and it will only attempt to process files that end with '.sts'. 


If you'd like to reduce a single .sts file, only use the code between the following lines:
    start:
        `lines_to_skip = next((i for i, line in enumerate(fin_mag, start=1) if '0  0' in line), None) - 1`
            (set `fin_mag` to be the appropriate path to the data file)
    end:
        `np.save(fpath__reduced_file, dat_mag_sph)`
            (set `fpath__reduced_file` to be the appropriate path to the output file)
Note that you might have to make additional adjustments for paths and logging. These should be fairly trivial.


The final data are saved as .npy files that can be loaded with `np.load`. This returns an Nx7 np.ndarray, where N is the number of data points, and the columns are:
    0: decimal days [since 2014-10-10 00:00:00]
    1: longitude    [-180, 180]
    2: latitude     [-90, 90]
    3: elevation    [km]
    4: B_theta      [nt]
    5: B_phi        [nt]
    6: B_r          [nt]
Although .npy files can't be opened with a text editor, they are significantly smaller than a text file containing the same data (3x smaller) and can be loaded extremely quickly. If you'd like to use the data with a different language, you can first load it with Python (`np.load`) and then save it in a different format (`np.savetxt` for .txt or .csv, or `scipy.io.savemat` for matfiles). The code would look something like this, generated from ChatGPT: https://gist.github.com/Humboldt-Penguin/363f5e9bfe42ad4596f135217e8d1bee. This conversion will require Python, but if you don't want to install anything, you can use the browser-based Google Colab editor (https://colab.research.google.com/). 



"""






############################################################################################################################################


from redplanet import utils
import numpy as np
# import pandas as pd
import zipfile
import os
import io
from datetime import datetime, timedelta
import logging


# OPTIONAL -- make a beeping sound when done running. I think this only works on Windows.
try:
    import winsound 
    import time
except:
    pass



############################################################################################################################################
"""user inputs"""

max_altitude_km = 200

# fpath__magzip = r'C:\Users\Eris\Documents\sync_local\00_Local\mars\data\maven\1_raw\maven.mag.calibrated-pc-highres\maven.mag.calibrated-pc-highres__2014.zip'
# fpath__magzip = r'C:\Users\Eris\Documents\sync_local\00_Local\mars\data\maven\1_raw\maven.mag.calibrated-pc-highres\maven.mag.calibrated-pc-highres__2015.zip'
# fpath__magzip = r'C:\Users\Eris\Documents\sync_local\00_Local\mars\data\maven\1_raw\maven.mag.calibrated-pc-highres\maven.mag.calibrated-pc-highres__2016.zip'
# fpath__magzip = r'C:\Users\Eris\Documents\sync_local\00_Local\mars\data\maven\1_raw\maven.mag.calibrated-pc-highres\maven.mag.calibrated-pc-highres__2017.zip'
# fpath__magzip = r'C:\Users\Eris\Documents\sync_local\00_Local\mars\data\maven\1_raw\maven.mag.calibrated-pc-highres\maven.mag.calibrated-pc-highres__2018.zip'
# fpath__magzip = r'C:\Users\Eris\Documents\sync_local\00_Local\mars\data\maven\1_raw\maven.mag.calibrated-pc-highres\maven.mag.calibrated-pc-highres__2019.zip'
# fpath__magzip = r'C:\Users\Eris\Documents\sync_local\00_Local\mars\data\maven\1_raw\maven.mag.calibrated-pc-highres\maven.mag.calibrated-pc-highres__2020.zip'
# fpath__magzip = r'C:\Users\Eris\Documents\sync_local\00_Local\mars\data\maven\1_raw\maven.mag.calibrated-pc-highres\maven.mag.calibrated-pc-highres__2021.zip'
# fpath__magzip = r'C:\Users\Eris\Documents\sync_local\00_Local\mars\data\maven\1_raw\maven.mag.calibrated-pc-highres\maven.mag.calibrated-pc-highres__2022.zip'
# fpath__magzip = r'C:\Users\Eris\Documents\sync_local\00_Local\mars\data\maven\1_raw\maven.mag.calibrated-pc-highres\maven.mag.calibrated-pc-highres__2023.zip'
'''
Path to a *zip file* containing maven mag data files, which has been downloaded from: https://drive.google.com/drive/folders/1iRJoprOsjB02DYjtk8wr8LExupcdWY5y?usp=sharing
    Note 1: 
        This zip file be a subset of the full 9-year dataset, such as a single year or month. The full dataset is ~300 GB zipped and >1 TB unzipped, so this functionality gives an easier way to reduce data without having a lot of free space on your computer or having to waste time unzipping files.
    Note 2: 
        That original source is https://pds-ppi.igpp.ucla.edu/search/view/?f=null&id=pds://PPI/maven.mag.calibrated/data/pc/highres, but we mirror data from each year on Google Drive for significantly faster download speeds.
'''


dirpath__reduced_parent = r'C:\Users\Eris\Documents\sync_local\00_Local\mars\data\maven\2_reduced'
'''
path to the parent folder where the reduced data will be saved (only a single folder will be created called 'maven.mag.calibrated-pc-highres__filters=200km/').
'''


############################################################################################################################################
"""setup"""

# times
start_datetime = datetime.now()


# paths
fpath__magzip = utils.getPath(fpath__magzip)
dirpath__reduced_parent = utils.getPath(dirpath__reduced_parent)
dirpath__reduced = utils.getPath(dirpath__reduced_parent, f'maven.mag.calibrated-pc-highres__filters={max_altitude_km}km')

os.makedirs(dirpath__reduced, exist_ok=True)


# logger
log_path = utils.getPath(dirpath__reduced, 'logs')
os.makedirs(log_path, exist_ok=True)
log_path = utils.getPath(log_path, f'log__{start_datetime.strftime("%y%m%d-%H%M")}__file={os.path.basename(os.path.splitext(os.path.basename(fpath__magzip))[0])}.txt')

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s", # format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # Output to console
        logging.FileHandler(log_path)  # Output to log file
    ]
)


logging.info(f'Running `maven_reducer_1_altitude.py`.')
logging.info(f'\tFor more information, see https://github.com/Humboldt-Penguin/redplanet.')
logging.info('')
logging.info(f'Started running at {start_datetime.strftime("%m/%d/%Y %H:%M")}')
logging.info('')
logging.info(f'Saving logs to {log_path}')
logging.info('')
logging.info(f'File to reduce: {fpath__magzip}')
logging.info('')
logging.info(f'Reduced data directory: {dirpath__reduced}')
logging.info('------------------------------------------------------------------------------------------')
logging.info('')








num_saved = 0

with zipfile.ZipFile(fpath__magzip, 'r') as magzip:
    
    # find number of files
    num_files = 0    
    for fname_mag in magzip.namelist():
        if fname_mag.endswith('.sts'):
            num_files += 1

    logging.info(f'Found {num_files} files.')
    runtime = timedelta(seconds=10)*num_files
    logging.info(f'Estimated runtime (assuming 10 sec/file): {str(runtime).split(".")[0]} (i.e. completed by {(datetime.now()+runtime).strftime("%m/%d/%Y %H:%M")}))')
    logging.info('')
    logging.info('')
    pad_digits = len(str(num_files))


    # process each file
    i_file = 1
    for fname_mag in magzip.namelist():
        if not fname_mag.endswith('.sts'):
            continue


        # setup
        checkpoint = datetime.now()

        year = int(fname_mag[-20:-16])
        month = int(fname_mag[-16:-14])
        day = int(fname_mag[-14:-12])

        dirpath__reduced_file = utils.getPath(dirpath__reduced, f'{year}', f'{month:02}')
        os.makedirs(dirpath__reduced_file, exist_ok=True)

        fname__reduced_file = f'mvn_mag_200km_{year}-{month:02}-{day:02}.npy'
        fpath__reduced_file = utils.getPath(dirpath__reduced_file, fname__reduced_file)



        logging.info(f'Processing {i_file:0{pad_digits}}/{num_files}...\t({fname__reduced_file})')
        i_file += 1


        if os.path.isfile(fpath__reduced_file):
            logging.info(f'\t- File already exists, deleting.')
            os.remove(fpath__reduced_file)


        # unzip/open the file and start working with it
        with magzip.open(fname_mag) as fin_mag:
            fin_mag = io.TextIOWrapper(fin_mag)

            # skip header and read data
            lines_to_skip = next((i for i, line in enumerate(fin_mag, start=1) if '0  0' in line), None) - 1
            dat_mag_cart = np.loadtxt(fin_mag, skiprows=lines_to_skip, usecols=(0,6,7,8,9,11,12,13))
            '''columns are initially: 0: year, 1: decimal day of year, 2: BX, 3: BY, 4: BZ, 5: posX, 6: posY, 7: posZ'''


            # convert to total decimal days since data collection started, starting with 0 on 2014-10-10 00:00:00
            dat_mag_cart[:,1] += (datetime(int(dat_mag_cart[0,0]), 1, 1) - datetime(2014,10,10)).days - 1 


            dat_mag_cart = dat_mag_cart[:, [1,5,6,7,2,3,4] ]
            '''
            `dat_mag_cart` columns are: 
                0: decimal days [since 2014-10-10 00:00:00]
                1: posX         [km]
                2: posY         [km]
                3: posZ         [km]
                4: BX           [nt]
                5: BY           [nt]
                6: BZ           [nt]
            '''


            # pre-compute useful values
            xy2 = dat_mag_cart[:,1]**2 + dat_mag_cart[:,2]**2              # xy2 = x^2 + y^2
            r2 = xy2 + dat_mag_cart[:,3]**2                                # r2  = x^2 + y^2 + z^2

            length1 = dat_mag_cart.shape[0]

            # altitude cut
            max_altitude = 200
            i_altitude_cut = np.where(r2 < ((3396.2+max_altitude)**2))[0]
            dat_mag_cart = dat_mag_cart[i_altitude_cut,:]
            xy2 = xy2[i_altitude_cut]
            r2 = r2[i_altitude_cut]

            length2 = dat_mag_cart.shape[0]
            logging.info(f'\t- Percent reduction: {(length1-length2)/length1*100:.2f}%')


            '''
            [Explanation for the following code...]

            DESCRIPTION
            ------------
                Convert cartesian position/vectors to spherical coordinates. 

            NOTES
            ------------
                ORTHOGONALITY: 
                    - Position conversion requires simple trig, but magnetic field vectors must be converted with a transformation matrix `D` in order to preserve orthogonality. 
                    - Orthogonality is important in this case because it means that the transformation between Cartesian and spherical coordinates maintains both the direction and magnitude of the vectors. In other words, vectors that were orthogonal in the Cartesian coordinate system will remain orthogonal in the spherical coordinate system. 

                COORDINATES:
                    - `theta` is the counterclockwise angle in the x-y plane measured in radians from the positive x-axis. The value of the angle is in the range [-pi pi].
                    - `phi` is the elevation angle in radians from the x-y plane. The value of the angle is in the range [-pi/2, pi/2].
                    - `r` is the elevation angle in radians from the x-y plane. The value of the angle is in the range [-pi/2, pi/2].
                (These make it so our transformation matrix is a bit different from the one on Wikipedia: https://en.wikipedia.org/wiki/Vector_fields_in_cylindrical_and_spherical_coordinates)

            '''

            dat_mag_sph = np.empty_like(dat_mag_cart)

            dat_mag_sph[:,0] = dat_mag_cart[:,0]                                   # decimal day
            theta = np.arctan2(dat_mag_cart[:,2], dat_mag_cart[:,1])               # theta = atan2(y,x)
            phi   = np.arctan2(dat_mag_cart[:,3], np.sqrt(xy2))                    # phi = atan2(z,sqrt(x^2+y^2))

            # precompute values
            sin_theta = np.sin(theta)
            sin_phi   = np.sin(phi)
            cos_theta = np.cos(theta)
            cos_phi   = np.cos(phi)

            # transformation matrix
            D = np.array([
                [  cos_theta * cos_phi ,      sin_theta * cos_phi ,     sin_phi              ],
                [ -sin_theta           ,      cos_theta           ,     np.zeros_like(theta) ],
                [ -cos_theta * sin_phi ,     -sin_theta * sin_phi ,     cos_phi              ]
            ])

            # transform magnetic field vectors
            dat_mag_sph[:,4:] = np.einsum('ijk,kj->ki', D, dat_mag_cart[:,4:])     # B_theta, B_phi, B_r

            # convert to longitude and latitude (degrees)
            dat_mag_sph[:,1:3] = np.degrees(np.array([theta, phi]).T)              # lon, lat
            dat_mag_sph[:,3] = np.sqrt(r2)                                         # r (elevation)

            '''
            `dat_mag_cart` columns are: 
                0: decimal days [since 2014-10-10 00:00:00]
                1: longitude    [-180, 180]
                2: latitude     [-90, 90]
                3: elevation    [km]
                4: B_theta      [nt]
                5: B_phi        [nt]
                6: B_r          [nt]
            '''

            np.save(fpath__reduced_file, dat_mag_sph)
            num_saved += 1



        delta = datetime.now()-checkpoint
        logging.info(f'\t- This process took: {str(delta).split(".")[0]}')



        logging.info('')



logging.info('')
logging.info('')
logging.info('------------------------------------------------------------------------------------------')
logging.info('Summary (sanity check):')
logging.info(f'* {num_files} data files in archive.')
logging.info(f'* {num_saved} datasets saved.')

logging.info('')
if (num_files == num_saved):
    logging.info('All is well :> \t(according to num_files==num_saved)')
else:
    logging.info('Something went wrong :< \t(according to num_files==num_saved)')
logging.info('------------------------------------------------------------------------------------------')
logging.info('')



''' finish logging '''


end_datetime = datetime.now()
logging.info(f'Finished running at {end_datetime.strftime("%m/%d/%Y %H:%M")}')
delta = end_datetime-start_datetime
logging.info(f'(Total execution time: {str(delta).split(".")[0]})')


logging.shutdown()


# notify when done
try:
    for i in range(5):
        winsound.Beep(500, 1000)
        time.sleep(0.5)
except:
    pass