#!/bin/bash
# Check that images referenced in posts are under 1MB (BlueSky limit)
# Auto-compress images that are too large

MAX_SIZE=1048576  # 1MB in bytes
EXIT_CODE=0
AUTO_COMPRESS=${AUTO_COMPRESS:-true}  # Set to false to disable auto-compression

echo "Checking image sizes in blog posts..."

# Find all markdown files in _posts
for post in _posts/*.markdown _posts/*.md; do
    [ -f "$post" ] || continue

    # Extract image field from front matter
    image=$(sed -n '/^---$/,/^---$/p' "$post" | grep '^image:' | sed 's/^image:[[:space:]]*//' | tr -d '\r' | tr -d '"')

    if [ -n "$image" ]; then
        # Remove leading slash if present to get relative path
        image_path="${image#/}"

        # Also check with leading dot for clarity
        if [ -f "$image_path" ]; then
            size=$(stat -c%s "$image_path" 2>/dev/null || stat -f%z "$image_path" 2>/dev/null)

            if [ "$size" -gt "$MAX_SIZE" ]; then
                size_mb=$(echo "scale=2; $size / 1048576" | bc)

                if [ "$AUTO_COMPRESS" = "true" ]; then
                    echo "🔄 Auto-compressing oversized image in $post"
                    echo "   Original: $image_path (${size_mb}MB)"

                    # Backup original
                    backup="${image_path}.backup"
                    cp "$image_path" "$backup"

                    # Get file extension
                    extension="${image_path##*.}"

                    # Compress using ImageMagick, progressively downscaling until under MAX_SIZE
                    if command -v convert &> /dev/null; then
                        if [ "$extension" = "png" ]; then
                            scale=90
                        else
                            scale=85
                            quality=80
                        fi

                        compressed=false
                        while [ "$scale" -ge 20 ]; do
                            if [ "$extension" = "png" ]; then
                                convert "$backup" -resize "${scale}%" -strip "$image_path"
                            else
                                convert "$backup" -resize "${scale}%" -quality "$quality" -strip "$image_path"
                            fi

                            new_size=$(stat -c%s "$image_path" 2>/dev/null || stat -f%z "$image_path" 2>/dev/null)
                            new_size_kb=$(echo "scale=1; $new_size / 1024" | bc)

                            if [ "$new_size" -le "$MAX_SIZE" ]; then
                                echo "   ✓ Compressed to ${new_size_kb}KB at ${scale}% scale (backup saved as ${backup})"
                                compressed=true
                                break
                            fi

                            new_size_mb=$(echo "scale=2; $new_size / 1048576" | bc)
                            echo "   ⚠ Still ${new_size_mb}MB at ${scale}% scale, downscaling further..."
                            scale=$((scale - 15))
                            if [ "$extension" != "png" ] && [ "$quality" -gt 40 ]; then
                                quality=$((quality - 10))
                            fi
                        done

                        if [ "$compressed" = "false" ]; then
                            echo "   ❌ Still too large after downscaling to ${scale}%. Manual intervention needed."
                            EXIT_CODE=1
                        fi
                    else
                        echo "   ❌ ImageMagick (convert) not found. Cannot auto-compress."
                        echo "   Install ImageMagick or set AUTO_COMPRESS=false"
                        EXIT_CODE=1
                    fi
                else
                    echo "❌ ERROR: Image too large in $post"
                    echo "   Image: $image_path (${size_mb}MB)"
                    echo "   Maximum allowed: 1MB for BlueSky compatibility"
                    EXIT_CODE=1
                fi
            else
                size_kb=$(echo "scale=1; $size / 1024" | bc)
                echo "✓ $post: $image_path (${size_kb}KB)"
            fi
        else
            echo "⚠ WARNING: Image not found: $image_path (referenced in $post)"
        fi
    fi
done

if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ All images are under 1MB"
else
    echo ""
    if [ "$AUTO_COMPRESS" = "true" ]; then
        echo "Build stopped: Some images could not be compressed automatically."
        echo "Check the errors above and compress manually. Backups are saved as *.backup"
    else
        echo "Build stopped: Please compress or replace large images before deploying."
        echo "Or set AUTO_COMPRESS=true to enable automatic compression."
    fi
fi

exit $EXIT_CODE
