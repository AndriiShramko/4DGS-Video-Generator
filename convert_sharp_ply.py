"""
Converter for SHARP PLY files to standard 3DGS format.
Removes incompatible elements (extrinsic, intrinsic, etc.) and keeps only vertex data.
"""

import sys
from pathlib import Path
import numpy as np
from plyfile import PlyData, PlyElement


def convert_sharp_ply_to_standard(input_path: Path, output_path: Path):
    """Converts SHARP PLY file to standard 3DGS format."""
    
    print(f"Reading PLY file: {input_path}")
    plydata = PlyData.read(input_path)
    
    # Find vertex element
    vertex_element = None
    for element in plydata.elements:
        if element.name == "vertex":
            vertex_element = element
            break
    
    if vertex_element is None:
        raise ValueError("Vertex element not found in PLY file")
    
    print(f"Found {len(vertex_element.data)} Gaussian elements")
    
    # Extract only vertex data (standard 3DGS format)
    # Format: x, y, z, f_dc_0, f_dc_1, f_dc_2, opacity, scale_0, scale_1, scale_2, rot_0, rot_1, rot_2, rot_3
    vertex_data = vertex_element.data
    
    # Create new PLY file with only vertex elements
    vertex_elements = PlyElement.describe(vertex_data, "vertex")
    
    # Save only vertex element (without extrinsic, intrinsic and others)
    new_plydata = PlyData([vertex_elements], text=False)
    
    print(f"Saving standard PLY file: {output_path}")
    new_plydata.write(output_path)
    
    print(f"Conversion completed successfully!")
    print(f"  File size: {output_path.stat().st_size / (1024*1024):.2f} MB")
    print(f"  Number of Gaussian elements: {len(vertex_data)}")
    
    return output_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_sharp_ply.py <input.ply> [output.ply]")
        print("Example: python convert_sharp_ply.py output_3dgs/image.ply output_3dgs/image_standard.ply")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)
    
    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        # Automatically create output filename
        output_path = input_path.parent / f"{input_path.stem}_standard.ply"
    
    try:
        convert_sharp_ply_to_standard(input_path, output_path)
        print(f"\nDone! File saved: {output_path}")
    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

