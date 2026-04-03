# # converter.py
# import os
# from app_2.utils.log import get_logger

# logger = get_logger(__name__, "converter_log.log")
# logger.info("Converter started")

# SVG_HEADER = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" stroke="black" stroke-width="{stroke}" fill="none">"""

# SVG_FOOTER = "</svg>"

# def element_to_svg(elem: dict) -> str:
#     """
#     Convert a single element dict to its SVG tag.
#     """
#     etype = elem.get("type")

#     if etype == "circle":
#         cx = elem["cx"]
#         cy = elem["cy"]
#         r = elem["r"]
#         return f'<circle cx="{cx}" cy="{cy}" r="{r}" />'

#     if etype == "line":
#         x1 = elem["x1"]
#         y1 = elem["y1"]
#         x2 = elem["x2"]
#         y2 = elem["y2"]
#         return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" />'

#     logger.warning(f"Unknown element type: {etype}")
#     return ""

# def json_to_svg(data: dict) -> str:
#     """
#     Convert structured JSON into an SVG string.
#     """
#     try:
#         size = data.get("canvas", "24")
#         stroke = data.get("stroke", 2)

#         svg_str = SVG_HEADER.format(size=size, stroke=stroke)

#         elements = data.get("elements", [])
#         for elem in elements:
#             svg_str += element_to_svg(elem)

#         svg_str += SVG_FOOTER
#         return svg_str

#     except Exception as e:
#         logger.error(f"Error in JSON→SVG conversion: {e}")
#         raise

# def save_svg(svg: str, output_path: str):
#     """
#     Save SVG content to a file.
#     """
#     try:
#         with open(output_path, "w", encoding="utf-8") as f:
#             f.write(svg)
#         logger.info(f"SVG saved: {output_path}")
#     except Exception as exc:
#         logger.error(f"Failed to save SVG: {exc}")
#         raise

# if __name__ == "__main__":
   
#     sample = {
#         "canvas": "24",
#         "stroke": 2,
#         "elements": [
#             {"type": "circle", "cx": 12, "cy": 12, "r": 8, "x1": None, "y1": None, "x2": None, "y2": None},
#             {"type": "line", "cx": None, "cy": None, "r": None, "x1": 16, "y1": 16, "x2": 22, "y2": 22}
#         ]
#     }
#     svg_data = json_to_svg(sample)
#     save_svg(svg_data, "./test_icon.svg")
#     print("Generated test_icon.svg")


#the new 3 phase strategy for complex svg generations and above is the simple circle and line for poc


# converter.py
import os
import re
from app_2.utils.log import get_logger

logger = get_logger(__name__, "converter_log.log")
logger.info("Converter started")

STYLE_ATTRS = {
    "fill": "fill",
    "stroke": "stroke",
    "strokeWidth": "stroke-width",
    "strokeLinecap": "stroke-linecap",
    "strokeLinejoin": "stroke-linejoin",
    "opacity": "opacity",
    "transform": "transform"
}

def sanitize_number(val) -> str:
    """Rounds floats to 2 decimal places to prevent float bleed."""
    if val is None:
        return ""
    try:
        val_float = float(val)
        if val_float.is_integer():
            return str(int(val_float))
        return f"{val_float:.2f}".rstrip("0").rstrip(".")
    except ValueError:
        return str(val)

def sanitize_path(d: str) -> str:
    """Removes invalid characters from path data."""
    if not d:
        return ""
    return re.sub(r'[^a-zA-Z0-9,\.\-\s]', '', d).strip()

def build_style_string(elem: dict) -> str:
    """Maps JSON camelCase styles to SVG kebab-case attributes."""
    styles = []
    for json_key, svg_key in STYLE_ATTRS.items():
        val = elem.get(json_key)
        if val is not None:
            styles.append(f'{svg_key}="{val}"')
    return " ".join(styles)

def render_element(elem: dict) -> str:
    """Recursively processes a JSON node into an SVG node."""
    if not isinstance(elem, dict) or "type" not in elem:
        logger.warning(f"Invalid element skipped: {elem}")
        return ""

    etype = elem["type"]
    styles = build_style_string(elem)
    style_str = f" {styles}" if styles else ""

    try:
        if etype == "circle":
            cx = sanitize_number(elem.get("cx", 0))
            cy = sanitize_number(elem.get("cy", 0))
            r = sanitize_number(elem.get("r", 0))
            return f'<circle cx="{cx}" cy="{cy}" r="{r}"{style_str} />'

        elif etype == "rect":
            x = sanitize_number(elem.get("x", 0))
            y = sanitize_number(elem.get("y", 0))
            w = sanitize_number(elem.get("width", 0))
            h = sanitize_number(elem.get("height", 0))
            rx_val = elem.get("rx")
            ry_val = elem.get("ry")
            rx_str = f' rx="{sanitize_number(rx_val)}"' if rx_val is not None else ""
            ry_str = f' ry="{sanitize_number(ry_val)}"' if ry_val is not None else ""
            return f'<rect x="{x}" y="{y}" width="{w}" height="{h}"{rx_str}{ry_str}{style_str} />'

        elif etype == "line":
            x1 = sanitize_number(elem.get("x1", 0))
            y1 = sanitize_number(elem.get("y1", 0))
            x2 = sanitize_number(elem.get("x2", 0))
            y2 = sanitize_number(elem.get("y2", 0))
            return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{style_str} />'

        elif etype == "path":
            d = sanitize_path(elem.get("d", ""))
            return f'<path d="{d}"{style_str} />'

        elif etype in ("polygon", "polyline"):
            points = elem.get("points", "")
            return f'<{etype} points="{points}"{style_str} />'

        elif etype == "g":
            children = elem.get("children", [])
            inner_svg = "".join(render_element(child) for child in children)
            return f'<g{style_str}>{inner_svg}</g>'

        else:
            logger.warning(f"Unknown element type: {etype}")
            return ""

    except Exception as e:
        logger.error(f"Error rendering element {etype}: {str(e)}")
        return ""

def render_defs(defs_list: list) -> str:
    """Generates the <defs> block for gradients and advanced fills."""
    if not defs_list:
        return ""

    defs_inner = []
    for item in defs_list:
        try:
            item_type = item.get("type")
            item_id = item.get("id")
            if not item_id or item_type not in ("linearGradient", "radialGradient"):
                continue

            coords = ""
            for k in ["x1", "y1", "x2", "y2", "cx", "cy", "r"]:
                if k in item and item[k] is not None:
                    coords += f' {k}="{item[k]}"'

            stops_str = ""
            for stop in item.get("stops", []):
                offset = stop.get("offset", "0%")
                scolor = stop.get("stopColor", "#000000")
                sopac = stop.get("stopOpacity")
                sopac_str = f' stop-opacity="{sanitize_number(sopac)}"' if sopac is not None else ""
                stops_str += f'<stop offset="{offset}" stop-color="{scolor}"{sopac_str} />'

            defs_inner.append(f'<{item_type} id="{item_id}"{coords}>{stops_str}</{item_type}>')

        except Exception as e:
            logger.error(f"Error rendering def element: {str(e)}")

    if not defs_inner:
        return ""
    return f"<defs>{''.join(defs_inner)}</defs>"

def json_to_svg(data: dict) -> str:
    """Primary pipeline compiler."""
    try:
        viewbox = data.get("viewBox", "0 0 24 24")
        svg_str = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}">'

        defs_list = data.get("defs")
        if defs_list:
            svg_str += render_defs(defs_list)

        elements = data.get("elements", [])
        for elem in elements:
            svg_str += render_element(elem)

        svg_str += "</svg>"
        return svg_str

    except Exception as e:
        logger.error(f"Error in JSON to SVG conversion: {str(e)}")
        raise

def save_svg(svg: str, output_path: str):
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg)
        logger.info(f"SVG saved: {output_path}")
    except Exception as exc:
        logger.error(f"Failed to save SVG: {exc}")
        raise

if __name__ == "__main__":
    test_json = {
        "viewBox": "0 0 24 24",
        "defs": [
            {
                "id": "grad1",
                "type": "linearGradient",
                "x1": "0%", "y1": "0%", "x2": "100%", "y2": "100%",
                "stops": [
                    {"offset": "0%", "stopColor": "#FF0000", "stopOpacity": 1},
                    {"offset": "100%", "stopColor": "#0000FF", "stopOpacity": 0.5}
                ]
            }
        ],
        "elements": [
            {
                "type": "g",
                "transform": "translate(2, 2)",
                "children": [
                    {"type": "rect", "x": 0, "y": 0, "width": 10, "height": 10, "rx": 2, "fill": "url(#grad1)"},
                    {"type": "path", "d": "M 5 5 L 15 15 Z", "stroke": "black", "strokeWidth": 1.5}
                ]
            }
        ]
    }
    
    try:
        result_svg = json_to_svg(test_json)
        save_svg(result_svg, "test_output.svg")
        print("Generated test_output.svg successfully.")
    except Exception as e:
        print(f"Error: {e}")