import os
import base64
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class ImageValidator:
    """
    Acts as a strict visual Quality Control gate using Groq's Vision models
    to prevent dirty data from reaching the segmentation phase.
    """
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables.")
        
        self.client = Groq(api_key=self.api_key)
        # Using Groq's current supported vision model
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct" 

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def validate_clean_plate(self, image_path: str) -> bool:
        print("DEBUG: Running Quality Control via Groq Vision...")
        try:
            base64_image = self._encode_image(image_path)
            
            # prompt = (
            #     "ROLE: You are a Lead Vision QA Engineer for a Vector Graphics Pipeline.\n"
            #     "TASK: Analyze the provided image against four strict 'Vector-Ready' criteria.\n\n"
                
            #     "CRITERIA:\n"
            #     "1. BACKGROUND_PURITY: The subject must be on a 100% solid, pure white (#FFFFFF) background. "
            #     "FAIL if there are any floating geometric lines, 'shrapnel', or background patterns.\n"
            #     "2. EDGE_CONTINUITY: The subject must have bold, closed-loop black outlines. "
            #     "FAIL if lines are 'fuzzy', pixelated, or have gaps that would cause color bleeding.\n"
            #     "3. TOPOLOGICAL_SIMPLICITY: The image must be flat 2D. "
            #     "FAIL if there are gradients, 3D shading, shadows, or realistic textures.\n"
            #     "4. NOISE_FLOOR: No 'micro-details' like thin whiskers or hair that cannot be vectorized easily.\n\n"
                
            #     "OUTPUT_FORMAT:\n"
            #     "You must provide a JSON-style response for internal parsing:\n"
            #     "{\n"
            #     "  'status': 'PASS' or 'FAIL',\n"
            #     "  'reasoning': 'Short technical explanation of the failure',\n"
            #     "  'noise_level': 'LOW/MED/HIGH'\n"
            #     "}\n"
            #     "Respond with ONLY the JSON object."
            # )
            prompt = (
                "ROLE: You are a Lead Vision QA Engineer for a Vector Graphics Pipeline.\n"
                "TASK: Analyze the provided image against four strict 'Vector-Ready' criteria.\n\n"
                
                "CRITERIA:\n"
                "1. BACKGROUND_PURITY: The subject must be on a 100% solid, pure white (#FFFFFF) background. "
                "FAIL if there are any floating geometric lines, 'shrapnel', or background patterns.\n"
                "2. EDGE_CONTINUITY: The subject must have bold, closed-loop black outlines. "
                "FAIL if lines are 'fuzzy', pixelated, or have gaps that would cause color bleeding.\n"
                "3. TOPOLOGICAL_SIMPLICITY: The image must be flat 2D. "
                "FAIL if there are gradients, 3D shading, shadows, or realistic textures.\n"
                "4. NOISE_FLOOR: No 'micro-details' like thin whiskers or hair that cannot be vectorized easily.\n\n"
                
                "OUTPUT_FORMAT:\n"
                "You must provide a JSON-style response for internal parsing:\n"
                "{\n"
                "  'status': 'PASS' or 'FAIL',\n"
                "  'reasoning': 'Short technical explanation of the failure',\n"
                "  'noise_level': 'LOW/MED/HIGH'\n"
                "}\n"
                "Respond with ONLY the JSON object."
            )
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                temperature=0.0, # Zero creativity, strict evaluation
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip().upper()
            print(f"Validation Result: {result}")
            
            return "PASS" in result

        except Exception as e:
            print(f"Validator Error: {str(e)}")
            return False