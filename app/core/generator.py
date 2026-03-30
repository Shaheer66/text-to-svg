import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

class VectorGenerator:
    """
    Phase 1 Core: AI Image Generation.
    Upgraded to Flux LoRA for Pro-grade (IconScout) flat vector foundations.
    """
    def __init__(self):
        self.api_key = os.getenv("HF_TOKEN")
        if not self.api_key:
            raise ValueError("FATAL ERROR: HF_TOKEN is missing in .env")
        
        # Pointing directly to the specialized Flux LoRA
        self.model_id = "renderartist/simplevectorflux"
        self.client = InferenceClient(model=self.model_id, token=self.api_key)

    def generate_specialized_vector(self, user_goal: str, output_path: str) -> str:
        """
        Active Generator: Uses simplevectorflux with strict prompt engineering.
        Produces high-contrast, zero-gradient assets ideal for OpenCV thresholding.
        """
        # CRITICAL: 'v3ct0r' trigger word must be included for the LoRA to activate
        refined_prompt = (
            f"v3ct0r, {user_goal}, flat vector art, minimalist clip art, "
            f"bold black outlines, solid white fill, no shading, "
            f"no gradients, pure white background, high contrast, crisp edges"
        )
        
        print(f"Status: Requesting specialized LoRA asset [{self.model_id}]...")
        print(f"Prompt injected: {refined_prompt}")
        
        try:
            # Flux models generally prefer lower guidance scales (3.0 - 4.5)
            image = self.client.text_to_image(
                refined_prompt,
                guidance_scale=3.5,
                num_inference_steps=28
            )
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            image.save(output_path)
            return output_path
            
        except Exception as e:
            raise RuntimeError(f"LoRA Generation Failed: {str(e)}")

    # =========================================================================
    # LEGACY ARCHIVE (Commented out for backtracking purposes)
    # ==========================================================



# import os
# from dotenv import load_dotenv
# from huggingface_hub import InferenceClient
# from PIL import Image
# from typing import Optional

# load_dotenv()

# class VectorGenerator:
#     """
#     Handles the synthesis of flat, high-contrast images using 
#     the official HF Inference Client for production stability.
#     """
    
#     def __init__(self):
#         # The library handles the routing to https://router.huggingface.co/ automatically
#         self.token = os.getenv("HF_TOKEN")
#         if not self.token:
#             raise ValueError("HF_TOKEN not found in environment variables.")
        
            
#         self.client = InferenceClient(
#             model="stabilityai/stable-diffusion-xl-base-1.0", 
#             token=self.token
#         )
        
#         self.base_v_constraints = (
#             "professional vector art, flat 2d design, minimalist icon, "
#             "bold thick black outlines, solid color fills, no gradients, "
#             "no shadows, no shading, clean sharp edges, isolated on a pure white background"
#             "STRICT white background, NO background patterns, NO geometric noise, "
#             "NO textures, NO floating artifacts, isolated on white, high-contrast"
#         )
#         # self.base_v_constraints = (
#         #     "Strictly follow the below rules to create a clean, flat 2D vector graphic that is perfectly isolated on a pure white background. "
#         #     "MASTER_STYLE: [Flat 2D Vector Graphic, Minimalist Iconography, Bold Outlines]. "
#         #     "TECHNICAL_SPECS: [Solid color fills, 100% pure white background (#FFFFFF), "
#         #     "high-contrast edges, no gradients, no shadows, no 3D effects, no textures]. "
#         #     "NEGATIVE_CONSTRAINTS: [NO background patterns, NO floating geometric lines, "
#         #     "NO stray particles, NO atmospheric noise, NO thin hair-like details, "
#         #     "NO complex shading, NO photographic elements]. "
#         #     "The subject must be perfectly centered and fully isolated on a clean white field."
#         # )

    

#     def generate_base_image(self, prompt: str, output_path: str) -> Optional[str]:
#         final_prompt = f"{prompt}, {self.base_v_constraints}"
        
#         try:
#             print(f"DEBUG: Requesting image from HF Router via InferenceClient...")
#             # The client handles the POST request and binary conversion
#             image = self.client.text_to_image(
#                 final_prompt,
#                 guidance_scale=8,
#                 num_inference_steps=40
#             )
            
#             os.makedirs(os.path.dirname(output_path), exist_ok=True)
#             image.save(output_path, "PNG")
#             return output_path
            
#         except Exception as e:
#             print(f"Production Error: {str(e)}")
#             return None