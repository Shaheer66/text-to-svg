# import cv2
# import numpy as np
# import os

# class SemanticSegmenter:
#     """
#     Transforms PNG assets into binary masks optimized for SVG tracing.
#     Uses Otsu's Thresholding and Morphological Closing to ensure solid shapes.
#     """
#     def generate_mask(self, input_path: str, output_path: str) -> str:
     
#         img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
#         if img is None:
#             raise FileNotFoundError(f"Source image not found at {input_path}")

#         #  unify edges and reduce 'whisker' artifacts
#         blurred = cv2.GaussianBlur(img, (5, 5), 0)

#         # Otsu Thresholding (Inverting so Subject=White, Background=Black)
#         _, mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

#         #  Morphological Closing: Fills small holes within the geometric shapes
#         kernel = np.ones((5, 5), np.uint8)
#         mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

#         os.makedirs(os.path.dirname(output_path), exist_ok=True)
#         cv2.imwrite(output_path, mask)
        
#         return output_path

import cv2
import numpy as np

class SemanticSegmenter:
    def generate_mask(self, input_path: str, output_path: str) -> str:
        img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
        
        # High-pass filter to keep ONLY the crisp black lines
        blurred = cv2.GaussianBlur(img, (3, 3), 0)
        # We want the lines to be WHITE for the tracer to follow them
        _, mask = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY_INV) 
        
        # Clean up stray pixels but keep the thin lines
        kernel = np.ones((2,2), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        cv2.imwrite(output_path, mask)
        return output_path


# import cv2
# import numpy as np
# import os

# class SemanticSegmenter:
#     def generate_mask(self, input_path: str, output_path: str) -> str:
#         img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
        
#         # 1. Standard Otsu to get the initial wireframe
#         blurred = cv2.GaussianBlur(img, (5, 5), 0)
#         _, mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

#         # 2. FILL LOGIC: Find all closed loops and fill them with white
#         # This turns the 'wireframe' into a 'solid shape'
#         contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
#         solid_mask = np.zeros_like(mask)
#         cv2.drawContours(solid_mask, contours, -1, 255, thickness=cv2.FILLED)

#         # 3. Final Cleaning (Remove tiny stray noise)
#         kernel = np.ones((3,3), np.uint8)
#         solid_mask = cv2.morphologyEx(solid_mask, cv2.MORPH_OPEN, kernel)

#         os.makedirs(os.path.dirname(output_path), exist_ok=True)
#         cv2.imwrite(output_path, solid_mask)
#         return output_path