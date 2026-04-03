# main.py

import os
import json
from dotenv import load_dotenv

from app_2.utils.log import get_logger

# Import your modules
from app_2.core.generator import generate_icon
from app_2.core.converter import json_to_svg, save_svg

# Initialize environment and logger
load_dotenv()
logger = get_logger(__name__, "main_log.log")
logger.info("Main orchestration started")

def run_pipeline(text_prompt: str, output_svg_path: str):
    """
    Orchestrate the text → JSON → SVG pipeline.
    """
    try:
        logger.info(f"Generating icon JSON for prompt: {text_prompt}")
        # Generate structured JSON via your generator
        icon_json = generate_icon(text_prompt)
        logger.info("JSON generation complete")

        # Log the JSON for debugging
        logger.debug(f"Generated JSON: {json.dumps(icon_json, indent=2)}")

        # Convert the JSON to SVG
        logger.info("Converting JSON to SVG")
        svg_content = json_to_svg(icon_json)

        # Save the SVG
        logger.info(f"Saving SVG to {output_svg_path}")
        save_svg(svg_content, output_svg_path)
        logger.info("SVG generation pipeline completed successfully")

    except Exception as e:
        logger.error(f"Error in pipeline: {e}")
        raise

if __name__ == "__main__":
   
    try:
        prompt = "stock icon"
        output_file = f"D:/projects/text-to-svg/app_2/data/output/{prompt.replace(' ', '_')}.svg"
        run_pipeline(prompt, output_file)
        logger.info("Pipeline executed successfully")

    except Exception as exc:
        logger.error(f"Unhandled exception in main: {exc}")