import numpy as np
from pathlib import Path

numpy_version = np.__version__

data_dir = Path('data')
data_file = data_dir / 'numpy_version.txt'

# Check if the directory exists, if not create it
data_dir.mkdir(parents=True, exist_ok=True)

# Check if the file exists and print the appropriate message
if data_file.exists():
    print(f"The file {data_file} already exists.")
else:
    print(f"The file {data_file} does not exist. It will be created now.")

# Write the numpy version to the file
with data_file.open('w') as file:
    file.write(numpy_version)

print(f"Numpy version {numpy_version} has been written to {data_file}")
