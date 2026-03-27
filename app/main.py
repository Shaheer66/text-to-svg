# from app.core.generator import VectorGenerator

# def run_step_1():
#     engine = VectorGenerator()
#     user_goal = "a minimalist geometric cat"
#     output_file = "data/output/step1_cat_base.png"
    
#     print(f"Step 1: Generating base asset for '{user_goal}'...")
#     result = engine.generate_base_image(user_goal, output_file)
    
#     if result:
#         print(f"Success. Asset saved to: {result}")
#     else:
#         print("Step 1 Failed.")

# if __name__ == "__main__":
#     run_step_1()


from app.core.generator import VectorGenerator
from app.utils.validator import ImageValidator

def run_step_1():
    engine = VectorGenerator()
    validator = ImageValidator()
    
    user_goal = "a minimalist geometric cat"
    output_file = "data/output/step1_cat_base.png"
    max_retries = 3
    
    for attempt in range(1, max_retries + 1):
        print(f"\n--- Attempt {attempt} of {max_retries} ---")
        print(f"Step 1: Generating base asset...")
        
        result_path = engine.generate_base_image(user_goal, output_file)
        
        if result_path:
            is_valid = validator.validate_clean_plate(result_path)
            if is_valid:
                print(f"Success! Final clean asset locked at: {result_path}")
                return True
            else:
                print("Validation Failed: Background noise detected. Retrying...")
        else:
            print("Generation Failed. Retrying...")
            
    print("Error: Max retries reached. Could not generate a clean plate.")
    return False

if __name__ == "__main__":
    run_step_1()