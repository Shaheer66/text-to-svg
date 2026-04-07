# # main.py

# import os
# import json
# from dotenv import load_dotenv

# from app_2.utils.log import get_logger

# # Import your modules
# from app_2.core.generator import generate_icon
# from app_2.core.converter import json_to_svg, save_svg

# # Initialize environment and logger
# load_dotenv()
# logger = get_logger(__name__, "main_log.log")
# logger.info("Main orchestration started")

# def run_pipeline(text_prompt: str, output_svg_path: str):
#     """
#     Orchestrate the text → JSON → SVG pipeline.
#     """
#     try:
#         logger.info(f"Generating icon JSON for prompt: {text_prompt}")
#         # Generate structured JSON via your generator
#         icon_json = generate_icon(text_prompt)
#         logger.info("JSON generation complete")

#         # Log the JSON for debugging
#         logger.debug(f"Generated JSON: {json.dumps(icon_json, indent=2)}")

#         # Convert the JSON to SVG
#         logger.info("Converting JSON to SVG")
#         svg_content = json_to_svg(icon_json)

#         # Save the SVG
#         logger.info(f"Saving SVG to {output_svg_path}")
#         save_svg(svg_content, output_svg_path)
#         logger.info("SVG generation pipeline completed successfully")

#     except Exception as e:
#         logger.error(f"Error in pipeline: {e}")
#         raise

# if __name__ == "__main__":
   
#     try:
#         prompt = "search icon"
#         output_file = f"D:/projects/text-to-svg/app_2/data/output/{prompt.replace(' ', '_')}.svg"
#         run_pipeline(prompt, output_file)
#         logger.info("Pipeline executed successfully")

#     except Exception as exc:
#         logger.error(f"Unhandled exception in main: {exc}")

#updated main.py below includes the data management and proper loging
# main.py
import os
import json
import hashlib
import pathlib
from datetime import datetime
from dotenv import load_dotenv

from app_2.utils.log import get_logger
from app_2.core.generator import generate_icon
from app_2.core.converter import json_to_svg, save_svg

load_dotenv()
logger = get_logger(__name__, "main_log.log")

# Machine-independent path anchoring
BASE_DIR = pathlib.Path(__file__).parent.resolve()
PATH_JSON = BASE_DIR / "data" / "output" / "json"
PATH_SVG = BASE_DIR / "data" / "output" / "svg"
PATH_PROMPT = BASE_DIR / "data" / "input" / "prompt"

# Ensure directory tree exists
for path in [PATH_JSON, PATH_SVG, PATH_PROMPT]:
    path.mkdir(parents=True, exist_ok=True)

def get_file_identifiers(text_prompt: str) -> str:
    """Generates a unique, sortable filename base."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prompt_hash = hashlib.sha256(text_prompt.encode()).hexdigest()[:5]
    return f"{timestamp}_{prompt_hash}"

def run_pipeline(text_prompt: str):
    """Orchestrates the Text -> JSON -> SVG pipeline with persistence."""
    try:
        file_id = get_file_identifiers(text_prompt)
        logger.info(f"Execution started | ID: {file_id} | Prompt: {text_prompt}")

        # 1. Persist Raw Prompt
        prompt_file = PATH_PROMPT / f"{file_id}.txt"
        with open(prompt_file, "w", encoding="utf-8") as f:
            f.write(text_prompt)

        #  Generate JSON (with internal guardrails)
        icon_json = generate_icon(text_prompt)
        json_file = PATH_JSON / f"{file_id}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(icon_json, f, indent=2)
        
        #  Convert to SVG
        svg_content = json_to_svg(icon_json)
        svg_file = PATH_SVG / f"{file_id}.svg"
        save_svg(svg_content, str(svg_file))

        logger.info(f"Pipeline Success | Files saved with ID: {file_id}")
        return str(svg_file)

    except Exception as e:
        logger.error(f"Pipeline Failure: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        user_input = "marketing campaign icon with megaphone and  graph realistic, detailed, human-drawn style"
        #user_input = "create a realistic icon of cat face with whiskers and pointy ears, it should looks like human drawn, think about in details, evaluate your answer and re-iterate it and get something out of the box"
        #user_input = "Tiger Icon, realistic, detailed, human-drawn style, with stripes and fierce expression"
        #user_input = "ChatGPT Icon, realistic, detailed, human-drawn style, with speech bubble and friendly expression"
        #user_input = "Search Icon, realistic, detailed, human-drawn style, with magnifying glass and subtle shadow"
        generated_path = run_pipeline(user_input)
        print(f"Process complete. Output: {generated_path}")
    except Exception as exc:
        print(f"Critical System Error: {exc}")