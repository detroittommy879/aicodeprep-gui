#!/usr/bin/env python3
"""
Convert aicp.svg to PNG with real transparency by removing background paths.
"""
import xml.etree.ElementTree as ET
import copy

# Read SVG
with open('aicp.svg', 'r') as f:
    svg_content = f.read()

# Parse
tree = ET.parse('aicp.svg')
root = tree.getroot()

# Build a list of elements to remove first (can't modify during iteration)
elements_to_remove = []

# Background fill colors to remove
background_fills = ['#e2e2de', '#e2e2e1', '#e2e2e2', '#e6e6e6', '#ebebeb', '#f3f3f3', '#f9f9f9', '#ffffff', '#000000']

def find_parents(elem, depth=0):
    """Recursively find and mark background elements"""
    if depth > 10:  # Safety limit
        return

    for child in list(elem):
        child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag

        if child_tag == 'path':
            d = child.get('d', '')
            fill = child.get('fill', '')

            # Check if it's a background rectangle (covers most of the 1024x434 canvas)
            if fill in background_fills:
                # Check for rectangular paths covering large areas
                if '0 0h1024' in d or '1024v434' in d or 'H0z' in d:
                    elements_to_remove.append((elem, child))
                    print(f"Found background path: fill={fill}")
                    continue

        elif child_tag == 'rect':
            elements_to_remove.append((elem, child))
            print(f"Found rect element")
            continue

        # Recurse
        find_parents(child, depth + 1)

# Find all background elements
find_parents(root)

# Remove them
for parent, child in elements_to_remove:
    try:
        parent.remove(child)
        print(f"Removed element")
    except ValueError:
        pass  # Already removed

print(f"\nTotal elements to remove: {len(elements_to_remove)}")

# Save cleaned SVG
tree.write('aicp_clean.svg', encoding='utf-8', xml_declaration=True)
print("Saved aicp_clean.svg")

# Now convert to PNG with real transparency using CairoSVG
import cairosvg

cairosvg.svg2png(
    url='aicp_clean.svg',
    write_to='aicp_transparent.png',
    dpi=300,
    background_color=None  # Transparent background
)

print("Converted to aicp_transparent.png with real transparency!")
