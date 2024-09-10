#!/bin/bash

# Initialize counter
counter=1

# Loop through all files, sorted by creation time (oldest first)
find . -maxdepth 1 -type f -not -name "*.sh" -print0 | while IFS= read -r -d '' file; do
    # Extract the extension
    ext="${file##*.}"

    # If the extension is not webp, skip the file
    if [[ "$ext" != "webp" ]]; then
        continue
    fi

    # Format the counter to be two digits
    formatted_counter=$(printf "%02d" $counter)

    # Rename the file with the new format "output_XX.webp"
    mv "$file" "output_${formatted_counter}.webp"

    # Increment the counter
    counter=$((counter + 1))
done
