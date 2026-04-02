import cv2
import os

class VectorTracer:
    """
    Step 3: Converts binary masks into mathematical SVG paths.
    """
    def trace_to_svg(self, mask_path: str, svg_path: str):
      
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        
        # 2. Extract external contours (The 'Mathematical Boundary')
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 3. Build the SVG XML String
        h, w = mask.shape
        svg_header = f'<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">'
        paths = []
        
        for cnt in contours:
            path_data = "M "
            for i, pt in enumerate(cnt):
                x, y = pt[0]
                path_data += f"{x},{y} "
                if i == 0: path_data += "L "
            path_data += "Z"
            paths.append(f'<path d="{path_data}" fill="black" stroke="none" />')
            
        svg_footer = "</svg>"
        full_svg = svg_header + "".join(paths) + svg_footer
        
         
        os.makedirs(os.path.dirname(svg_path), exist_ok=True)
        with open(svg_path, "w") as f:
            f.write(full_svg)
            
        return svg_path
    

    #using the vtracer##########

import vtracer
import os

class VectorTracer:
    """
    Production-grade Vectorizer using the VisionCortex VTracer engine.
    Handles high-accuracy wireframes without 'bleeding' internal details.
    """
    def trace_to_svg(self, mask_path: str, svg_path: str):
        # Ensure output directory exists
        os.makedirs(os.path.dirname(svg_path), exist_ok=True)

        # Final Verdict Logic: 
        # We use 'binary' mode for the mask and 'cutout' to preserve internal holes.
        vtracer.convert_image_to_svg_py(
            mask_path, 
            svg_path,
            colormode = 'binary',     # Target B&W wireframes
            hierarchical = 'cutout',  # KEY: Subtracts holes so eyes/facets stay clear
            mode = 'spline',          # Uses Pro-level Bezier curves instead of jagged lines
            filter_speckle = 4,       # Ignores tiny noise pixels
            color_precision = 8,      # Max accuracy
            layer_difference = 16,
            corner_threshold = 60,    # Keeps geometric corners sharp
            length_threshold = 4.0,   # Removes shaky micro-lines
            max_iterations = 10       # Optimization depth
        )
        
        return svg_path    


# #fill with white color

# import cv2
# import os

# class VectorTracer:
#     """
#     Advanced Tracer: Captures internal geometry for detailed SVGs.
#     """
#     def trace_to_svg(self, mask_path: str, svg_path: str):
#         mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
#         h, w = mask.shape
        
#         # RETR_TREE captures the 'parent-child' relationship of lines
#         contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
#         svg_header = f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
#         paths = []
        
#         if hierarchy is not None:
#             for i, cnt in enumerate(contours):
#                 # Logic: If a contour has a parent, it's a 'hole' (fill it with white or skip)
#                 # For this minimalist look, we will draw all significant contours
#                 if cv2.contourArea(cnt) < 20: continue # Ignore tiny noise dots
                
#                 path_data = "M "
#                 for j, pt in enumerate(cnt):
#                     x, y = pt[0]
#                     path_data += f"{x},{y} "
#                     if j == 0: path_data += "L "
#                 path_data += "Z"
                
#                 # Determine color: Top-level is black, internal 'holes' are white
#                 color = "black" if hierarchy[0][i][3] == -1 else "white"
#                 paths.append(f'<path d="{path_data}" fill="{color}" />')
            
#         full_svg = svg_header + "".join(paths) + "</svg>"
        
#         os.makedirs(os.path.dirname(svg_path), exist_ok=True)
#         with open(svg_path, "w") as f:
#             f.write(full_svg)
#         return svg_path





###black svg
# import cv2

# class VectorTracer:
#     def trace_to_svg(self, mask_path: str, svg_path: str):
#         mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
#         # Use approxPolyDP to make the lines "Smooth" and "Pro" like IconScout
#         contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
        
#         h, w = mask.shape
#         svg_content = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">']
        
#         for cnt in contours:
#             if cv2.contourArea(cnt) < 5: continue # Filter noise
#             # Simplify path to reduce file size and jagged edges
#             epsilon = 0.002 * cv2.arcLength(cnt, True)
#             approx = cv2.approxPolyDP(cnt, epsilon, True)
            
#             path_data = "M " + " L ".join([f"{p[0][0]},{p[0][1]}" for p in approx]) + " Z"
#             svg_content.append(f'<path d="{path_data}" fill="black" />')
            
#         svg_content.append("</svg>")
#         with open(svg_path, "w") as f:
#             f.write("".join(svg_content))
#         return svg_path