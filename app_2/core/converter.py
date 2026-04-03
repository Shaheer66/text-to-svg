# converter.py
import os
from app_2.utils.log import get_logger

logger = get_logger(__name__, "converter_log.log")
logger.info("Converter started")

SVG_HEADER = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" stroke="black" stroke-width="{stroke}" fill="none">"""

SVG_FOOTER = "</svg>"

def element_to_svg(elem: dict) -> str:
    """
    Convert a single element dict to its SVG tag.
    """
    etype = elem.get("type")

    if etype == "circle":
        cx = elem["cx"]
        cy = elem["cy"]
        r = elem["r"]
        return f'<circle cx="{cx}" cy="{cy}" r="{r}" />'

    if etype == "line":
        x1 = elem["x1"]
        y1 = elem["y1"]
        x2 = elem["x2"]
        y2 = elem["y2"]
        return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" />'

    logger.warning(f"Unknown element type: {etype}")
    return ""

def json_to_svg(data: dict) -> str:
    """
    Convert structured JSON into an SVG string.
    """
    try:
        size = data.get("canvas", "24")
        stroke = data.get("stroke", 2)

        svg_str = SVG_HEADER.format(size=size, stroke=stroke)

        elements = data.get("elements", [])
        for elem in elements:
            svg_str += element_to_svg(elem)

        svg_str += SVG_FOOTER
        return svg_str

    except Exception as e:
        logger.error(f"Error in JSON→SVG conversion: {e}")
        raise

def save_svg(svg: str, output_path: str):
    """
    Save SVG content to a file.
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg)
        logger.info(f"SVG saved: {output_path}")
    except Exception as exc:
        logger.error(f"Failed to save SVG: {exc}")
        raise

if __name__ == "__main__":
   
    sample = {
        "canvas": "24",
        "stroke": 2,
        "elements": [
            {"type": "circle", "cx": 12, "cy": 12, "r": 8, "x1": None, "y1": None, "x2": None, "y2": None},
            {"type": "line", "cx": None, "cy": None, "r": None, "x1": 16, "y1": 16, "x2": 22, "y2": 22}
        ]
    }
    svg_data = json_to_svg(sample)
    save_svg(svg_data, "./test_icon.svg")
    print("Generated test_icon.svg")