import cv2
import numpy as np

class ColorSegmenter:
    def extract_color_layers(self, input_path: str, num_colors: int = 4):
        img = cv2.imread(input_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        data = img_rgb.reshape((-1, 3)).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.1)
        _, label, centers = cv2.kmeans(data, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        centers = np.uint8(centers)
        labels_reshaped = label.reshape(img_rgb.shape[:2])
        
        layers = []
        for i in range(num_colors):
            mask = (labels_reshaped == i).astype(np.uint8) * 255
            
            # LOGIC: Identify Background
            # If the color occupies the corners, we flag it as 'is_background'
            is_bg = False
            if mask[0,0] > 0 and mask[0,-1] > 0 and mask[-1,0] > 0:
                is_bg = True
                
            hex_color = '#{:02x}{:02x}{:02x}'.format(*centers[i])
            layers.append({"mask": mask, "color": hex_color, "is_bg": is_bg})
            
        return layers