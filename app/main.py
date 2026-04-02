# main code for full pipeline
# import os
# import shutil
# from app.core.generator import VectorGenerator
# from app.core.segmenter import SemanticSegmenter
# from app.core.tracer import VectorTracer

# def run_full_pipeline():
    
#     asset_dir = "data/assets"
#     output_dir = "data/output"
    
#     reference_img = os.path.join(asset_dir, "image_2.png")
#     base_img = os.path.join(output_dir, "image_2.png")
#     mask_img = os.path.join(output_dir, "image_2_mask.png")
#     svg_output = os.path.join(output_dir, "image_2_final.svg")
    
#     engine = VectorGenerator()
#     segmentor = SemanticSegmenter()
#     tracer = VectorTracer()
    
#     user_goal = "cat"
    
#     os.makedirs(output_dir, exist_ok=True)

#     # --- PHASE 1: GENERATION (With Reference Fallback) ---
#     print("\n--- Phase 1 | Specialized Vector Synthesis ---")
#     try:
#         # Attempt to use the new Flux LoRA
#         result_path = engine.generate_specialized_vector(user_goal, base_img)
#         print(f"Success: Pro-grade asset generated at {result_path}")
#     except Exception as e:
#         print(f"API Warning: {str(e)}")
#         print("Status: Model is likely cold or timed out. Falling back to Reference Asset...")
        
#         if not os.path.exists(reference_img):
#             print(f"FATAL ERROR: Reference image not found at {reference_img}")
#             return False
            
#         shutil.copy2(reference_img, base_img)
#         print(f"Success: Reference asset synced to {base_img}")

#     # --- PHASE 2: SEMANTIC SEGMENTATION ---
#     print("\n--- Phase 2 | Semantic Segmentation ---")
#     try:
#         mask_path = segmentor.generate_mask(base_img, mask_img)
#         print(f"Success: Binary mask generated at {mask_path}")
#     except Exception as e:
#         print(f"FATAL ERROR: Phase 2 Failed: {str(e)}")
#         return False

#     # --- PHASE 3: VECTORIZATION ---
#     print("\n--- Phase 3 | Vectorization ---")
#     try:
#         final_svg = tracer.trace_to_svg(mask_img, svg_output)
#         print(f"PIPELINE COMPLETE: Pro-grade SVG generated at {final_svg}")
#         return True
#     except Exception as e:
#         print(f"FATAL ERROR: Phase 3 Failed: {str(e)}")
#         return False

# if __name__ == "__main__":
#     run_full_pipeline()


#previous version to backtrack

# from app.core.generator import VectorGenerator
# from app.core.segmenter import SemanticSegmenter
# from app.utils.validator import ImageValidator

# def run_full_pipeline():
#     engine = VectorGenerator()
#     validator = ImageValidator()
#     segmentor = SemanticSegmenter()
    
#     user_goal = "a minimalist geometric cat"
#     output_file = "data/output/step1_cat_base.png"
#     mask_img = "data/output/step2_mask.png"
#     max_retries = 3
    
#     # --- PHASE 1: GENERATION & VALIDATION ---
#     phase1_success = False
#     valid_image_path = None
    
#     for attempt in range(1, max_retries + 1):
#         print(f"\n--- Phase 1 | Attempt {attempt} of {max_retries} ---")
#         print("Status: Generating base asset...")
        
#         result_path = engine.generate_base_image(user_goal, output_file)
        
#         if result_path:
#             is_valid = validator.validate_clean_plate(result_path)
#             if is_valid:
#                 print(f"Success: Clean asset locked at {result_path}")
#                 valid_image_path = result_path
#                 phase1_success = True
#                 break  # Exit the retry loop and proceed to Phase 2
#             else:
#                 print("Warning: Validation Failed. Retrying...")
#         else:
#             print("Warning: Generation API Failed. Retrying...")

#     # Gatekeeper: Abort if Phase 1 completely failed
#     if not phase1_success:
#         print("\nFATAL ERROR: Max retries reached. Could not generate a clean plate. Pipeline aborted.")
#         return False

#     #  PHASE 2: SEMANTIC SEGMENTATION Mask Generator
#     print("\n--- Phase 2 | Semantic Segmentation ---")
#     print("Status: Generating Binary Mask...")
#     try:
#         mask_path = segmentor.generate_mask(valid_image_path, mask_img)
#         print(f"Success: Binary mask locked at {mask_path}")
#         return True
#     except Exception as e:
#         print(f"FATAL ERROR: Phase 2 Exception: {str(e)}")
#         return False

# if __name__ == "__main__":
#     run_full_pipeline()





#to test the specific classes
import os
import shutil
from app.core.generator import VectorGenerator 
from app.core.segmenter import SemanticSegmenter
from app.utils.validator import ImageValidator  
from app.core.tracer import VectorTracer

def run_full_pipeline():
    # Setup Paths
    asset_dir = "data/assets"
    output_dir = "data/output"
    svg_output = "data/output/step3_3_final.svg"
    
    
    reference_img = os.path.join(asset_dir, "gemini_sample.png")
    base_img = os.path.join(output_dir, "gemini_sample.png")
    mask_img = os.path.join(output_dir, "gemini_sample_2_mask.png")
    svg_output = os.path.join(output_dir, "gemini_sample_2_final.svg")
    
   
    segmentor = SemanticSegmenter()
    tracer = VectorTracer()
    
    segmentor = SemanticSegmenter()
    tracer = VectorTracer()
    
    # --- PHASE 1: ASSET LOCKING ---
    print("\n--- Phase 1 | Asset Locking ---")
    if not os.path.exists(reference_img):
        print(f"FATAL ERROR: Reference image not found at {reference_img}")
        return False
        
    os.makedirs(output_dir, exist_ok=True)
    shutil.copy2(reference_img, base_img)
    print(f"Success: Reference asset synced to {base_img}")

    # --- PHASE 2: SEMANTIC SEGMENTATION ---
    print("\n--- Phase 2 | Semantic Segmentation ---")
    try:
        mask_path = segmentor.generate_mask(base_img, mask_img)
        print(f"Success: Binary mask generated at {mask_path}")
    except Exception as e:
        print(f"FATAL ERROR: Phase 2 Failed: {str(e)}")
        return False

    # --- PHASE 3: VECTORIZATION ---
    print("\n--- Phase 3 | Vectorization ---")
    try:
        final_svg = tracer.trace_to_svg(mask_img, svg_output)
        print(f"PIPELINE COMPLETE: SVG generated at {final_svg}")
        return True
    except Exception as e:
        print(f"FATAL ERROR: Phase 3 Failed: {str(e)}")
        return False

if __name__ == "__main__":
    run_full_pipeline()