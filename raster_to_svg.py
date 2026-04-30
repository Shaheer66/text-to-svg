import io
import copy
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from lxml import etree
import cairosvg
import vtracer


SVG_NS = "http://www.w3.org/2000/svg"
NS = {"svg": SVG_NS}

RENDER_TAGS = {
    f"{{{SVG_NS}}}path",
    f"{{{SVG_NS}}}polygon",
    f"{{{SVG_NS}}}polyline",
    f"{{{SVG_NS}}}rect",
    f"{{{SVG_NS}}}circle",
    f"{{{SVG_NS}}}ellipse",
}


def preprocess_image(input_path: str, max_side: int = 2400) -> bytes:
    img = Image.open(input_path).convert("RGBA")

    # Flatten transparency safely
    bg = Image.new("RGBA", img.size, "white")
    bg.alpha_composite(img)
    img = bg.convert("RGB")

    # Light denoise only, do not destroy detail
    img = img.filter(ImageFilter.MedianFilter(size=3))

    # Optional controlled upscale for small raster images
    w, h = img.size
    if max(w, h) < 1200:
        scale = min(2, max_side / max(w, h))
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def vectorize(img_bytes: bytes) -> str:
    return vtracer.convert_raw_image_to_svg(
        img_bytes,
        img_format="png",
        colormode="color",
        hierarchical="cutout",
        mode="spline",
        filter_speckle=4,
        color_precision=7,
        layer_difference=16,
        corner_threshold=60,
        length_threshold=4.5,
        max_iterations=12,
        splice_threshold=55,
        path_precision=9,
    )


def is_hidden(el) -> bool:
    style = el.get("style", "").replace(" ", "").lower()
    attrs = {k.lower(): str(v).lower() for k, v in el.attrib.items()}

    hidden_signals = [
        "display:none",
        "visibility:hidden",
        "opacity:0",
        "fill-opacity:0",
        "stroke-opacity:0",
    ]

    if any(x in style for x in hidden_signals):
        return True

    if attrs.get("display") == "none":
        return True
    if attrs.get("visibility") == "hidden":
        return True
    if attrs.get("opacity") == "0":
        return True

    fill = attrs.get("fill", "")
    stroke = attrs.get("stroke", "")
    if fill in ("none", "transparent") and stroke in ("none", "transparent", ""):
        return True

    return False


def remove_basic_garbage(root):
    removed = 0

    for el in list(root.iter()):
        if el.tag in RENDER_TAGS and is_hidden(el):
            parent = el.getparent()
            if parent is not None:
                parent.remove(el)
                removed += 1

    return removed


def render_svg_to_alpha(svg_bytes: bytes, width: int, height: int) -> np.ndarray:
    png = cairosvg.svg2png(
        bytestring=svg_bytes,
        output_width=width,
        output_height=height,
    )
    img = Image.open(io.BytesIO(png)).convert("RGBA")
    return np.array(img)[:, :, 3] > 8


def render_single_element_mask(root, target_id: str, width: int, height: int) -> np.ndarray:
    temp = copy.deepcopy(root)

    for el in temp.iter():
        if el.tag in RENDER_TAGS:
            if el.get("data-clean-id") != target_id:
                el.set("display", "none")

    return render_svg_to_alpha(etree.tostring(temp), width, height)


def remove_invisible_layers(root, width: int, height: int, min_visible_px: int = 6):
    elements = [el for el in root.iter() if el.tag in RENDER_TAGS]

    for i, el in enumerate(elements):
        el.set("data-clean-id", str(i))

    removed_ids = set()
    covered = np.zeros((height, width), dtype=bool)

    # SVG paint order: later elements are on top
    for el in reversed(elements):
        eid = el.get("data-clean-id")

        try:
            mask = render_single_element_mask(root, eid, width, height)
        except Exception:
            continue

        total_px = int(mask.sum())
        if total_px == 0:
            removed_ids.add(eid)
            continue

        visible_px = int((mask & ~covered).sum())

        # Remove if fully or almost fully buried
        if visible_px < min_visible_px:
            removed_ids.add(eid)
        else:
            covered |= mask

    removed = 0
    for el in list(root.iter()):
        if el.tag in RENDER_TAGS and el.get("data-clean-id") in removed_ids:
            parent = el.getparent()
            if parent is not None:
                parent.remove(el)
                removed += 1

    for el in root.iter():
        el.attrib.pop("data-clean-id", None)

    return removed


def clean_svg(svg_text: str, output_path: str) -> dict:
    parser = etree.XMLParser(remove_blank_text=True, recover=True)
    root = etree.fromstring(svg_text.encode("utf-8"), parser)

    width = int(float(root.get("width", "1024").replace("px", "")))
    height = int(float(root.get("height", "1024").replace("px", "")))

    basic_removed = remove_basic_garbage(root)

    # Raster-mask occlusion cleanup
    hidden_removed = remove_invisible_layers(
        root,
        width=width,
        height=height,
        min_visible_px=max(4, int((width * height) * 0.000002)),
    )

    etree.ElementTree(root).write(
        output_path,
        pretty_print=False,
        xml_declaration=True,
        encoding="utf-8",
    )

    return {
        "basic_removed": basic_removed,
        "hidden_removed": hidden_removed,
    }


def vectorize_clean(input_image: str, output_svg: str):
    img_bytes = preprocess_image(input_image)
    raw_svg = vectorize(img_bytes)
    stats = clean_svg(raw_svg, output_svg)
    return stats


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("input_image")
    ap.add_argument("output_svg")
    args = ap.parse_args()

    stats = vectorize_clean(args.input_image, args.output_svg)
    print(f"Saved: {args.output_svg}")
    print(stats)