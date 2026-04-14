import vtracer
import os
import re

class ColorVectorTracer:
    def _extract_path_data(self, svg_content):
        match = re.search(r'd="([^"]+)"', svg_content)
        return match.group(1) if match else ""

    def assemble_svg(self, layers, output_path):
        h, w = layers[0]['mask'].shape
        # IMPORTANT: Start with a TRANSPARENT background, not a solid one
        svg_header = f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg">'
        path_elements = []

        for i, layer in enumerate(layers):
            # THE FIX: If the segmenter identified this color as the background, we SKIP it.
            if layer.get("is_bg", False):
                print(f"Skipping background layer: {layer['color']}")
                continue

            temp_mask = f"temp_{i}.png"
            temp_svg = f"temp_{i}.svg"
            import cv2
            cv2.imwrite(temp_mask, layer["mask"])

            vtracer.convert_image_to_svg_py(
                temp_mask,
                temp_svg,
                colormode = 'binary',
                hierarchical = 'cutout', # Keep internal detail
                mode = 'spline'
            )

            if os.path.exists(temp_svg):
                with open(temp_svg, "r") as f:
                    path_data = self._extract_path_data(f.read())
                    if path_data:
                        # Append only the foreground color paths
                        path_elements.append(f'<path d="{path_data}" fill="{layer["color"]}" />')

            # Cleanup
            for f in [temp_mask, temp_svg]:
                if os.path.exists(f): os.remove(f)

        full_svg = svg_header + "".join(path_elements) + "</svg>"
        with open(output_path, "w") as f:
            f.write(full_svg)
        
        return output_path