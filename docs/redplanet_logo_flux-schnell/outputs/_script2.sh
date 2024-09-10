for file in *; do
    if [[ -f "$file" && "$file" != *.* ]]; then
        mv -- "$file" "$file.webp"
    fi
done
