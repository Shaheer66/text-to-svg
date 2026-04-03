# generator.py
import os
import json
import logging
from groq import Groq
from dotenv import load_dotenv
from app_2.prompts.generator_prompt import prompt
from app_2.json_schema.schema import schema_v1
from app_2.utils.log import get_logger
 
load_dotenv()
logger = get_logger(__name__, "generator_logs.log")
logger.info("Generator started")
 
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    logger.error("GROQ_API_KEY is not set in environment variables.")
    raise EnvironmentError("GROQ_API_KEY is missing. Please set it in your .env file.")

client = Groq(api_key=API_KEY)
schema = schema_v1
 
def generate_icon(user_input: str) -> dict:
    """
    Generate an icon using Groq API based on the user input.
    
    Args:
        user_input (str): Description of the icon to generate.

    Returns:
        dict: JSON data according to schema.
    """
    try:
        logger.info(f"Generating icon for input: {user_input}")
        
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "icon_schema",
                    "strict": True,
                    "schema": schema
                }
            }
        )
 
        content = response.choices[0].message.content
        data = json.loads(content)
        logger.info(f"Icon generation successful for input: {user_input}")
        return data

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        raise ValueError(f"Failed to parse JSON from API response: {e}")

    except Exception as e:
        logger.error(f"Error generating icon: {e}")
        raise RuntimeError(f"Failed to generate icon: {e}")

 
if __name__ == "__main__":
    test_input = "generate a search icon"
    try:
        result = generate_icon(test_input)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")