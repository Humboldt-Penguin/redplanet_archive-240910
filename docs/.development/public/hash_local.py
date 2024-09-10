"""
SAMPLE USE: 
    Take file path "path/to/file.txt" as input; calculate file hash and save to "path/to/file.txt.md5" (or .sha256, .xxh3_64, etc.).
"""

import hashlib
import xxhash
from pathlib import Path
import tqdm


# def calculate_hashes(fpath, chunk_size=/1024 * 1024):
def calculate_hashes(fpath, chunk_size=65_536):
    hashes = {
        'md5': hashlib.md5(),
        # 'sha256': hashlib.sha256(),
        # 'xxh3_64': xxhash.xxh3_64()
    }

    file_size = fpath.stat().st_size

    with fpath.open('rb') as f:
        for chunk in tqdm.tqdm(iter(lambda: f.read(chunk_size), b''), total=file_size // chunk_size, unit='MB'):
            for hash_obj in hashes.values():
                hash_obj.update(chunk)
    
    return {name: hash_obj.hexdigest() for name, hash_obj in hashes.items()}


def save_hash_file(hash_value, hash_file_path):
    hash_file_path.write_text(hash_value)


def handle_existing_hash_file(hash_file_path, new_hash):
    old_hash = hash_file_path.read_text().strip()
    
    if old_hash != new_hash:
        previous_hash_file_path = hash_file_path.with_suffix(hash_file_path.suffix + ".PREVIOUS")
        hash_file_path.rename(previous_hash_file_path)
        print(f"Warning: Hash mismatch for {hash_file_path}. Previous hash saved as {previous_hash_file_path}")


def process_file(fpath):
    fpath = Path(fpath)
    base_path = fpath.parent
    file_name = fpath.name
    
    hashes = calculate_hashes(fpath)
    
    for hash_type, hash_value in hashes.items():
        hash_file_path = base_path / f"{file_name}.{hash_type}"
        
        if hash_file_path.exists():
            handle_existing_hash_file(hash_file_path, hash_value)
        
        save_hash_file(hash_value, hash_file_path)


def process_files(fpaths):
    for fpath in fpaths:
        process_file(fpath)





''' ######################################################################## '''
'''                                   Main                                   '''
''' ######################################################################## '''


# fpath = r'C:\Users\Eris\AppData\Local\redplanet\redplanet\Cache\Crust\topo\Mars_MGS_MOLA_DEM_mosaic_global_463m.tif'
# process_file(fpath)


''' ————————————————————————————— Original TIFs ———————————————————————————— '''

fpaths = [
    r"C:\Users\Eris\AppData\Local\redplanet\redplanet\Cache\Crust\topo\Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif",
    r"C:\Users\Eris\AppData\Local\redplanet\redplanet\Cache\Crust\topo\Mars_MGS_MOLA_DEM_mosaic_global_463m.tif",
]

process_files(fpaths)