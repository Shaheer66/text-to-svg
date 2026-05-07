import os
import re
import uuid
import json
import math
import html
import xml.etree.ElementTree as ET

import cv2
import torch
import numpy as np
from PIL import Image, ImageDraw

from model import load_model, get_pipe
from utils import convert_png_to_svg

try:
    from svgpathtools import svg2paths2
    from shapely.geometry import (
        Polygon,
        MultiPolygon,
        GeometryCollection,
        LineString,
        box,
    )
    from shapely.ops import unary_union

    try:
        from shapely.validation import make_valid
    except Exception:
        make_valid = None

except ImportError as e:
    raise ImportError(
        "Missing dependency. Install with:\n"
        "pip install svgpathtools shapely opencv-python numpy pillow"
    ) from e


# ============================================================
# Setup
# ============================================================

OUTPUT_DIR = "./outputs"
DEBUG_DIR = os.path.join(OUTPUT_DIR, "debug")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DEBUG_DIR, exist_ok=True)

device = "cuda" if torch.cuda.is_available() else "cpu"

load_model()
pipe = get_pipe()


# ============================================================
# Config
# ============================================================

GEN_SIZE = 512
WORK_SIZE = 1536

SVG_FLATTEN_STEP_PX = 0.9
MAX_SAMPLES_PER_SUBPATH = 3000

WALL_BRIGHTNESS_THRESHOLD = 220

GAP_CLOSE_PASSES_PX = [0.8, 1.4, 2.2, 3.2, 4.5]
FILL_OVERPAINT_PX = 3.0

MIN_FACE_AREA_PX = 18
MAX_FACE_AREA_RATIO = 0.94

FILL_SIMPLIFY_PX = 0.35
LINE_SIMPLIFY_PX = 0.15

PALETTE_SIZE = 8
MIN_LOCAL_COLOR_PIXELS = 40

WHITE_THRESHOLD = 246
BLACK_THRESHOLD = 36
MIN_SATURATION = 8

DEFAULT_PALETTE = [
    (255, 199, 44),
    (230, 57, 70),
    (0, 166, 81),
    (30, 144, 255),
    (128, 70, 36),
    (244, 210, 160),
    (255, 132, 40),
    (120, 120, 120),
]


# ============================================================
# Prompt Helpers
# ============================================================

def build_bw_prompt(prompt):
    return (
        f"{prompt}, clean black and white line art, icon or illustration, "
        f"clear bold black outlines, closed readable shapes, white background, "
        f"no color, no gray shading, no texture"
    )


def build_color_prompt(prompt):
    return (
        f"Color the provided black and white line drawing only. {prompt}. "
        f"Keep the exact same composition, pose, proportions, line placement, "
        f"and black outlines. Fill the existing enclosed areas with clean flat "
        f"vector-style colors. Do not redraw. Do not move outlines. Do not add "
        f"new details. No gradients, no shadows, no texture, white background."
    )


# ============================================================
# Generation
# ============================================================

def generate_bw_and_svg(prompt, reference_image_path=None):
    file_id = uuid.uuid4().hex

    ref_image = None
    if reference_image_path:
        ref_image = Image.open(reference_image_path).convert("RGB").resize(
            (GEN_SIZE, GEN_SIZE)
        )

    generator = torch.Generator(device=device).manual_seed(0)

    kwargs = dict(
        prompt=build_bw_prompt(prompt),
        height=GEN_SIZE,
        width=GEN_SIZE,
        guidance_scale=1.0,
        num_inference_steps=4,
        generator=generator,
    )

    if ref_image is not None:
        kwargs["image"] = ref_image

    result = pipe(**kwargs)
    image = result.images[0]

    bw_path = os.path.join(OUTPUT_DIR, f"{file_id}_bw.png")
    svg_path = os.path.join(OUTPUT_DIR, f"{file_id}.svg")

    image.save(bw_path, "PNG")
    convert_png_to_svg(bw_path, svg_path)

    print("[OK] Generated B/W image and SVG")
    print("BW :", bw_path)
    print("SVG:", svg_path)

    return file_id


def generate_color_reference(file_id, prompt):
    bw_path = os.path.join(OUTPUT_DIR, f"{file_id}_bw.png")

    if not os.path.exists(bw_path):
        raise FileNotFoundError(bw_path)

    bw_image = Image.open(bw_path).convert("RGB").resize((GEN_SIZE, GEN_SIZE))
    generator = torch.Generator(device=device).manual_seed(1)

    result = pipe(
        prompt=build_color_prompt(prompt),
        image=bw_image,
        height=GEN_SIZE,
        width=GEN_SIZE,
        guidance_scale=2.0,
        num_inference_steps=12,
        generator=generator,
    )

    color_image = result.images[0]

    color_path = os.path.join(OUTPUT_DIR, f"{file_id}_color.png")
    color_image.save(color_path, "PNG")

    print("[OK] Colored reference saved:", color_path)
    return color_path


# ============================================================
# Basic SVG / Color Utilities
# ============================================================

def parse_style(style_text):
    out = {}
    if not style_text:
        return out

    for item in style_text.split(";"):
        if ":" not in item:
            continue
        k, v = item.split(":", 1)
        out[k.strip().lower()] = v.strip()

    return out


def effective_attr(attrs, key, default=None):
    key = key.lower()
    style = parse_style(attrs.get("style", ""))
    if key in style:
        return style[key]
    return attrs.get(key, default)


def svg_number(value, default=0.0):
    if value is None:
        return default

    value = str(value).strip()
    match = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", value)

    if not match:
        return default

    try:
        return float(match.group(0))
    except Exception:
        return default


def parse_svg_viewbox(svg_attrs):
    vb = svg_attrs.get("viewBox") or svg_attrs.get("viewbox")

    if vb:
        nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", vb)
        if len(nums) >= 4:
            return tuple(float(x) for x in nums[:4])

    width = svg_number(svg_attrs.get("width"), GEN_SIZE)
    height = svg_number(svg_attrs.get("height"), GEN_SIZE)

    return 0.0, 0.0, width, height


def parse_color(value):
    if value is None:
        return None

    value = str(value).strip().lower()

    if value in ("none", "transparent"):
        return None

    named = {
        "black": (0, 0, 0, 1.0),
        "white": (255, 255, 255, 1.0),
        "red": (255, 0, 0, 1.0),
        "green": (0, 128, 0, 1.0),
        "blue": (0, 0, 255, 1.0),
    }

    if value in named:
        return named[value]

    if value.startswith("#"):
        h = value[1:]

        if len(h) == 3:
            try:
                r = int(h[0] * 2, 16)
                g = int(h[1] * 2, 16)
                b = int(h[2] * 2, 16)
                return r, g, b, 1.0
            except Exception:
                return None

        if len(h) in (6, 8):
            try:
                r = int(h[0:2], 16)
                g = int(h[2:4], 16)
                b = int(h[4:6], 16)
                a = 1.0
                if len(h) == 8:
                    a = int(h[6:8], 16) / 255.0
                return r, g, b, a
            except Exception:
                return None

    if value.startswith("rgb"):
        nums = re.findall(r"[-+]?\d*\.?\d+%?", value)

        if len(nums) >= 3:
            vals = []
            for n in nums[:3]:
                if n.endswith("%"):
                    vals.append(round(float(n[:-1]) * 2.55))
                else:
                    vals.append(round(float(n)))

            alpha = 1.0
            if len(nums) >= 4:
                a = nums[3]
                if a.endswith("%"):
                    alpha = float(a[:-1]) / 100.0
                else:
                    alpha = float(a)

            return (
                int(np.clip(vals[0], 0, 255)),
                int(np.clip(vals[1], 0, 255)),
                int(np.clip(vals[2], 0, 255)),
                float(np.clip(alpha, 0.0, 1.0)),
            )

    return None


def is_wall_paint(value, default_if_missing=False):
    if value is None or str(value).strip() == "":
        return default_if_missing

    value = str(value).strip().lower()

    if value in ("none", "transparent"):
        return False

    color = parse_color(value)

    if color is None:
        return default_if_missing

    r, g, b, a = color

    if a <= 0.01:
        return False

    brightness = 0.299 * r + 0.587 * g + 0.114 * b

    return brightness < WALL_BRIGHTNESS_THRESHOLD


def rgb_to_hex(rgb):
    r, g, b = [int(np.clip(x, 0, 255)) for x in rgb]
    return f"#{r:02x}{g:02x}{b:02x}"


def safe_make_valid(geom):
    if geom is None:
        return GeometryCollection()

    if geom.is_empty:
        return geom

    try:
        if not geom.is_valid:
            if make_valid is not None:
                geom = make_valid(geom)
            else:
                geom = geom.buffer(0)
    except Exception:
        try:
            geom = geom.buffer(0)
        except Exception:
            return GeometryCollection()

    try:
        if not geom.is_valid:
            geom = geom.buffer(0)
    except Exception:
        pass

    return geom


def geometry_polygons(geom):
    if geom is None or geom.is_empty:
        return []

    if isinstance(geom, Polygon):
        return [geom]

    if isinstance(geom, MultiPolygon):
        return list(geom.geoms)

    if isinstance(geom, GeometryCollection):
        out = []
        for g in geom.geoms:
            out.extend(geometry_polygons(g))
        return out

    return []


# ============================================================
# SVG Path Flattening and Wall Geometry
# ============================================================

def dedupe_coords(coords, eps=1e-7):
    if not coords:
        return []

    out = [coords[0]]

    for p in coords[1:]:
        last = out[-1]
        if abs(p[0] - last[0]) > eps or abs(p[1] - last[1]) > eps:
            out.append(p)

    return out


def sample_svg_path(subpath, sample_step_units):
    try:
        length = float(subpath.length(error=1e-4))
    except Exception:
        try:
            length = float(subpath.length())
        except Exception:
            length = sample_step_units * 20

    if not math.isfinite(length) or length <= 0:
        length = sample_step_units * 20

    n = max(8, int(math.ceil(length / max(sample_step_units, 1e-6))))
    n = min(n, MAX_SAMPLES_PER_SUBPATH)

    coords = []

    for i in range(n + 1):
        t = i / float(n)
        try:
            z = subpath.point(t)
        except Exception:
            continue

        x = float(np.real(z))
        y = float(np.imag(z))

        if math.isfinite(x) and math.isfinite(y):
            coords.append((x, y))

    return dedupe_coords(coords)


def polygon_from_coords(coords):
    if len(coords) < 3:
        return None

    if coords[0] != coords[-1]:
        coords = coords + [coords[0]]

    try:
        poly = Polygon(coords)
    except Exception:
        return None

    if poly.is_empty or abs(poly.area) < 1e-8:
        return None

    poly = safe_make_valid(poly)

    if poly.is_empty:
        return None

    return poly


def evenodd_rings_to_geometry(rings):
    rings = [r for r in rings if r is not None and not r.is_empty]

    if not rings:
        return GeometryCollection()

    rings = sorted(rings, key=lambda g: abs(g.area), reverse=True)

    geom = GeometryCollection()

    for ring in rings:
        ring = safe_make_valid(ring)

        if ring.is_empty:
            continue

        try:
            geom = geom.symmetric_difference(ring)
            geom = safe_make_valid(geom)
        except Exception:
            continue

    return safe_make_valid(geom)


def get_path_paint_roles(attrs):
    fill_value = effective_attr(attrs, "fill")
    stroke_value = effective_attr(attrs, "stroke")

    # SVG default: fill is black when fill/stroke are both absent.
    default_fill_black = fill_value is None and stroke_value is None

    fill_is_wall = is_wall_paint(fill_value, default_if_missing=default_fill_black)
    stroke_is_wall = is_wall_paint(stroke_value, default_if_missing=False)

    return fill_is_wall, stroke_is_wall


def path_to_wall_geometries(path, attrs, sample_step_units):
    fill_is_wall, stroke_is_wall = get_path_paint_roles(attrs)

    if not fill_is_wall and not stroke_is_wall:
        return []

    try:
        subpaths = path.continuous_subpaths()
    except Exception:
        subpaths = [path]

    geoms = []
    rings = []

    for subpath in subpaths:
        coords = sample_svg_path(subpath, sample_step_units)

        if len(coords) < 2:
            continue

        if fill_is_wall:
            poly = polygon_from_coords(coords)
            if poly is not None and not poly.is_empty:
                rings.append(poly)

        if stroke_is_wall:
            try:
                line = LineString(coords)
                if not line.is_empty and line.length > 0:
                    sw = svg_number(effective_attr(attrs, "stroke-width"), 1.0)
                    stroke_geom = line.buffer(
                        max(sw / 2.0, 0.25),
                        cap_style=1,
                        join_style=1,
                    )
                    stroke_geom = safe_make_valid(stroke_geom)
                    if not stroke_geom.is_empty:
                        geoms.append(stroke_geom)
            except Exception:
                pass

    if rings:
        fill_geom = evenodd_rings_to_geometry(rings)
        if not fill_geom.is_empty:
            geoms.append(fill_geom)

    return geoms


def build_black_line_path_element(path, attrs):
    fill_is_wall, stroke_is_wall = get_path_paint_roles(attrs)

    if not fill_is_wall and not stroke_is_wall:
        return None

    d = attrs.get("d")

    if not d:
        try:
            d = path.d()
        except Exception:
            return None

    d = html.escape(d, quote=True)

    transform = attrs.get("transform")
    transform_xml = ""
    if transform:
        transform_xml = f' transform="{html.escape(transform, quote=True)}"'

    if fill_is_wall and stroke_is_wall:
        sw = svg_number(effective_attr(attrs, "stroke-width"), 1.0)
        return (
            f'<path d="{d}"{transform_xml} fill="#000000" '
            f'stroke="#000000" stroke-width="{sw:g}" '
            f'stroke-linecap="round" stroke-linejoin="round" '
            f'fill-rule="evenodd"/>'
        )

    if fill_is_wall:
        return (
            f'<path d="{d}"{transform_xml} fill="#000000" '
            f'stroke="none" fill-rule="evenodd"/>'
        )

    sw = svg_number(effective_attr(attrs, "stroke-width"), 1.0)
    return (
        f'<path d="{d}"{transform_xml} fill="none" stroke="#000000" '
        f'stroke-width="{sw:g}" stroke-linecap="round" '
        f'stroke-linejoin="round"/>'
    )


def extract_svg_topology(svg_path):
    paths, attrs_list, svg_attrs = svg2paths2(svg_path)

    viewbox = parse_svg_viewbox(svg_attrs)
    min_x, min_y, vb_w, vb_h = viewbox

    units_per_px = max(vb_w, vb_h) / float(GEN_SIZE)
    sample_step_units = SVG_FLATTEN_STEP_PX * units_per_px

    wall_geoms = []
    line_items = []

    for path, attrs in zip(paths, attrs_list):
        geoms = path_to_wall_geometries(path, attrs, sample_step_units)

        if geoms:
            wall_geoms.extend(geoms)

        line_item = build_black_line_path_element(path, attrs)
        if line_item:
            line_items.append(line_item)

    if not wall_geoms:
        raise ValueError("No black/vector wall geometry detected in SVG.")

    wall_raw = unary_union(wall_geoms)
    wall_raw = safe_make_valid(wall_raw)

    canvas = box(min_x, min_y, min_x + vb_w, min_y + vb_h)
    wall_raw = safe_make_valid(wall_raw.intersection(canvas.buffer(10 * units_per_px)))

    line_body = "\n".join(line_items)

    return {
        "viewbox": viewbox,
        "units_per_px": units_per_px,
        "wall_raw": wall_raw,
        "line_body": line_body,
        "path_count": len(paths),
        "wall_geom_count": len(wall_geoms),
    }


# ============================================================
# Vector Face Extraction
# ============================================================

def geom_to_svg_path_data(geom):
    paths = []

    for poly in geometry_polygons(geom):
        if poly.is_empty:
            continue

        parts = []

        exterior = list(poly.exterior.coords)
        if len(exterior) >= 3:
            parts.append(f"M {exterior[0][0]:.3f} {exterior[0][1]:.3f}")
            for x, y in exterior[1:]:
                parts.append(f"L {x:.3f} {y:.3f}")
            parts.append("Z")

        for interior in poly.interiors:
            coords = list(interior.coords)
            if len(coords) >= 3:
                parts.append(f"M {coords[0][0]:.3f} {coords[0][1]:.3f}")
                for x, y in coords[1:]:
                    parts.append(f"L {x:.3f} {y:.3f}")
                parts.append("Z")

        if parts:
            paths.append(" ".join(parts))

    return paths


def extract_faces_for_gap(wall_raw, viewbox, units_per_px, gap_px):
    min_x, min_y, vb_w, vb_h = viewbox
    canvas = box(min_x, min_y, min_x + vb_w, min_y + vb_h)

    gap_units = gap_px * units_per_px
    border_eps = max(0.75 * units_per_px, 1e-6)

    try:
        wall_for_faces = wall_raw.buffer(
            gap_units,
            cap_style=1,
            join_style=1,
        )
        wall_for_faces = safe_make_valid(wall_for_faces.intersection(canvas))
    except Exception:
        wall_for_faces = safe_make_valid(wall_raw.intersection(canvas))

    free_space = safe_make_valid(canvas.difference(wall_for_faces))

    min_area_units = MIN_FACE_AREA_PX * units_per_px * units_per_px
    max_area_units = canvas.area * MAX_FACE_AREA_RATIO

    border_region = canvas.boundary.buffer(border_eps)

    faces = []

    for poly in geometry_polygons(free_space):
        poly = safe_make_valid(poly)

        if poly.is_empty:
            continue

        area = abs(poly.area)

        if area < min_area_units:
            continue

        if area > max_area_units:
            continue

        # This removes outer background and leaked regions connected to canvas.
        if poly.intersects(border_region):
            continue

        faces.append(poly)

    faces = sorted(faces, key=lambda g: abs(g.area), reverse=True)

    return faces


def extract_vector_faces(wall_raw, viewbox, units_per_px):
    min_x, min_y, vb_w, vb_h = viewbox
    canvas_area = vb_w * vb_h

    best_faces = []
    best_score = -1e9
    best_gap = None

    for gap_px in GAP_CLOSE_PASSES_PX:
        faces = extract_faces_for_gap(wall_raw, viewbox, units_per_px, gap_px)

        if not faces:
            score = -1e9 + gap_px
        else:
            area_ratio = sum(abs(f.area) for f in faces) / max(canvas_area, 1e-6)

            # Prefer more valid regions and good covered area,
            # but penalize excessive gap closing.
            score = (
                min(len(faces), 400) * 2.0
                + area_ratio * 70.0
                - gap_px * 2.2
            )

        if score > best_score:
            best_score = score
            best_faces = faces
            best_gap = gap_px

    return best_faces, best_gap


# ============================================================
# Palette and Color Assignment
# ============================================================

def load_rgb(path, size):
    return np.array(
        Image.open(path).convert("RGB").resize((size, size), Image.LANCZOS)
    )


def clean_color_pixels(pixels):
    if pixels.size == 0:
        return pixels

    pixels = pixels.astype(np.uint8)

    r = pixels[:, 0].astype(np.float32)
    g = pixels[:, 1].astype(np.float32)
    b = pixels[:, 2].astype(np.float32)

    brightness = 0.299 * r + 0.587 * g + 0.114 * b
    saturation = pixels.max(axis=1) - pixels.min(axis=1)

    keep = (
        (brightness > BLACK_THRESHOLD)
        & (brightness < WHITE_THRESHOLD)
        & (saturation >= MIN_SATURATION)
    )

    filtered = pixels[keep]

    if len(filtered) < MIN_LOCAL_COLOR_PIXELS:
        keep = (brightness > BLACK_THRESHOLD) & (brightness < WHITE_THRESHOLD)
        filtered = pixels[keep]

    return filtered


def extract_global_palette(color_rgb, k=PALETTE_SIZE):
    pixels = color_rgb.reshape(-1, 3)
    pixels = clean_color_pixels(pixels)

    if len(pixels) < 100:
        return DEFAULT_PALETTE[:]

    if len(pixels) > 60000:
        rng = np.random.default_rng(42)
        idx = rng.choice(len(pixels), size=60000, replace=False)
        pixels = pixels[idx]

    data = pixels.astype(np.float32)

    k = min(k, max(2, len(data) // 50))

    criteria = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
        40,
        0.8,
    )

    try:
        _, labels, centers = cv2.kmeans(
            data,
            k,
            None,
            criteria,
            4,
            cv2.KMEANS_PP_CENTERS,
        )
    except Exception:
        return DEFAULT_PALETTE[:]

    labels = labels.reshape(-1)
    counts = np.bincount(labels, minlength=k)

    order = np.argsort(-counts)

    palette = []

    for i in order:
        c = centers[i]
        c = np.round(c / 8) * 8
        rgb = tuple(int(np.clip(x, 0, 255)) for x in c)

        too_close = False
        for existing in palette:
            dist = np.linalg.norm(np.array(rgb) - np.array(existing))
            if dist < 28:
                too_close = True
                break

        if not too_close:
            palette.append(rgb)

    if not palette:
        palette = DEFAULT_PALETTE[:]

    while len(palette) < 4:
        palette.append(DEFAULT_PALETTE[len(palette) % len(DEFAULT_PALETTE)])

    return palette[:PALETTE_SIZE]


def save_palette_debug(file_id, palette):
    sw = 60
    h = 60
    img = Image.new("RGB", (sw * len(palette), h), "white")
    draw = ImageDraw.Draw(img)

    for i, color in enumerate(palette):
        draw.rectangle([i * sw, 0, (i + 1) * sw, h], fill=color)

    path = os.path.join(DEBUG_DIR, f"{file_id}_palette.png")
    img.save(path)
    return path


def coords_to_pixels(coords, viewbox, size):
    min_x, min_y, vb_w, vb_h = viewbox

    pts = []

    for x, y in coords:
        px = int(round((x - min_x) / vb_w * (size - 1)))
        py = int(round((y - min_y) / vb_h * (size - 1)))
        pts.append([px, py])

    return np.array(pts, dtype=np.int32)


def rasterize_geom_mask(geom, viewbox, size=WORK_SIZE):
    mask = np.zeros((size, size), dtype=np.uint8)

    for poly in geometry_polygons(geom):
        if poly.is_empty:
            continue

        exterior = coords_to_pixels(list(poly.exterior.coords), viewbox, size)

        if len(exterior) >= 3:
            cv2.fillPoly(mask, [exterior], 255)

        for interior in poly.interiors:
            hole = coords_to_pixels(list(interior.coords), viewbox, size)
            if len(hole) >= 3:
                cv2.fillPoly(mask, [hole], 0)

    return mask


def nearest_palette_color(rgb, palette):
    arr = np.array(palette, dtype=np.float32)
    rgb = np.array(rgb, dtype=np.float32)

    diff = arr - rgb[None, :]
    dist = np.sum(diff * diff, axis=1)
    idx = int(np.argmin(dist))

    return palette[idx]


def palette_vote_color(pixels, palette):
    if len(pixels) == 0:
        return None, 0.0

    if len(pixels) > 8000:
        stride = max(1, len(pixels) // 8000)
        pixels = pixels[::stride]

    p = pixels.astype(np.float32)
    pal = np.array(palette, dtype=np.float32)

    diff = p[:, None, :] - pal[None, :, :]
    dist = np.sum(diff * diff, axis=2)
    nearest = np.argmin(dist, axis=1)

    counts = np.bincount(nearest, minlength=len(palette))
    best_idx = int(np.argmax(counts))

    confidence = float(counts[best_idx]) / max(float(len(pixels)), 1.0)

    return palette[best_idx], confidence


def assign_region_color(face, color_rgb, palette, viewbox, region_index):
    mask = rasterize_geom_mask(face, viewbox, WORK_SIZE)

    if cv2.countNonZero(mask) == 0:
        return DEFAULT_PALETTE[region_index % len(DEFAULT_PALETTE)], {
            "source": "fallback_empty_mask",
            "confidence": 0.0,
            "pixels": 0,
        }

    kernel = np.ones((5, 5), np.uint8)

    safe_mask = cv2.erode(mask, kernel, iterations=2)

    if cv2.countNonZero(safe_mask) < MIN_LOCAL_COLOR_PIXELS:
        safe_mask = cv2.erode(mask, kernel, iterations=1)

    if cv2.countNonZero(safe_mask) < MIN_LOCAL_COLOR_PIXELS:
        safe_mask = mask

    pixels = color_rgb[safe_mask > 0]
    pixels = clean_color_pixels(pixels)

    if len(pixels) < MIN_LOCAL_COLOR_PIXELS:
        expanded = cv2.dilate(mask, np.ones((13, 13), np.uint8), iterations=1)
        pixels = color_rgb[expanded > 0]
        pixels = clean_color_pixels(pixels)

    if len(pixels) >= MIN_LOCAL_COLOR_PIXELS:
        voted, conf = palette_vote_color(pixels, palette)

        if voted is not None and conf >= 0.22:
            return voted, {
                "source": "local_palette_vote",
                "confidence": conf,
                "pixels": int(len(pixels)),
            }

        med = np.median(pixels, axis=0)
        nearest = nearest_palette_color(med, palette)

        return nearest, {
            "source": "local_median_palette_snap",
            "confidence": conf,
            "pixels": int(len(pixels)),
        }

    fallback = palette[region_index % len(palette)]

    return fallback, {
        "source": "fallback_palette_cycle",
        "confidence": 0.0,
        "pixels": int(len(pixels)),
    }


# ============================================================
# SVG Output
# ============================================================

def build_line_body_from_wall_geometry(wall_raw, units_per_px):
    simplify_units = LINE_SIMPLIFY_PX * units_per_px

    wall = safe_make_valid(
        wall_raw.simplify(simplify_units, preserve_topology=True)
    )

    items = []

    for d in geom_to_svg_path_data(wall):
        d = html.escape(d, quote=True)
        items.append(
            f'<path d="{d}" fill="#000000" stroke="none" fill-rule="evenodd"/>'
        )

    return "\n".join(items)


def validate_svg_string(svg_text):
    try:
        ET.fromstring(svg_text)
        return True, None
    except ET.ParseError as e:
        return False, str(e)


def create_debug_region_svg(file_id, viewbox, faces, line_body):
    min_x, min_y, vb_w, vb_h = viewbox
    rng = np.random.default_rng(123)

    paths = []

    for idx, face in enumerate(faces):
        color = rng.integers(40, 235, size=3)
        color_hex = rgb_to_hex(color)

        for d in geom_to_svg_path_data(face):
            d = html.escape(d, quote=True)
            paths.append(
                f'<path d="{d}" fill="{color_hex}" '
                f'stroke="none" fill-rule="evenodd" data-region="{idx}"/>'
            )

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{GEN_SIZE}" height="{GEN_SIZE}" viewBox="{min_x:g} {min_y:g} {vb_w:g} {vb_h:g}" xmlns="http://www.w3.org/2000/svg">
  <rect x="{min_x:g}" y="{min_y:g}" width="{vb_w:g}" height="{vb_h:g}" fill="white"/>
  <g id="debug-vector-faces">
    {chr(10).join(paths)}
  </g>
  <g id="line-art">
    {line_body}
  </g>
</svg>
'''

    path = os.path.join(DEBUG_DIR, f"{file_id}_vector_faces_debug.svg")

    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)

    return path


def build_colored_svg(file_id):
    bw_path = os.path.join(OUTPUT_DIR, f"{file_id}_bw.png")
    color_path = os.path.join(OUTPUT_DIR, f"{file_id}_color.png")
    svg_path = os.path.join(OUTPUT_DIR, f"{file_id}.svg")
    final_svg_path = os.path.join(OUTPUT_DIR, f"{file_id}_colored.svg")

    for p in [bw_path, color_path, svg_path]:
        if not os.path.exists(p):
            raise FileNotFoundError(p)

    topology = extract_svg_topology(svg_path)

    viewbox = topology["viewbox"]
    units_per_px = topology["units_per_px"]
    wall_raw = topology["wall_raw"]
    line_body = topology["line_body"]

    if not line_body.strip():
        line_body = build_line_body_from_wall_geometry(wall_raw, units_per_px)

    faces, selected_gap_px = extract_vector_faces(
        wall_raw,
        viewbox,
        units_per_px,
    )

    color_rgb = load_rgb(color_path, WORK_SIZE)
    palette = extract_global_palette(color_rgb, PALETTE_SIZE)
    palette_path = save_palette_debug(file_id, palette)

    min_x, min_y, vb_w, vb_h = viewbox
    canvas = box(min_x, min_y, min_x + vb_w, min_y + vb_h)

    overpaint_units = FILL_OVERPAINT_PX * units_per_px
    simplify_units = FILL_SIMPLIFY_PX * units_per_px

    fill_items = []
    region_meta = []

    faces = sorted(faces, key=lambda g: abs(g.area), reverse=True)

    for idx, face in enumerate(faces):
        color, color_meta = assign_region_color(
            face,
            color_rgb,
            palette,
            viewbox,
            idx,
        )

        fill_geom = face.buffer(
            overpaint_units,
            cap_style=1,
            join_style=1,
        )

        fill_geom = safe_make_valid(fill_geom.intersection(canvas))
        fill_geom = safe_make_valid(
            fill_geom.simplify(simplify_units, preserve_topology=True)
        )

        face_paths = geom_to_svg_path_data(fill_geom)

        for d in face_paths:
            d = html.escape(d, quote=True)
            fill_items.append(
                f'<path d="{d}" fill="{rgb_to_hex(color)}" '
                f'stroke="none" fill-rule="evenodd" data-region="{idx}"/>'
            )

        region_meta.append(
            {
                "region": idx,
                "area": float(abs(face.area)),
                "fill": rgb_to_hex(color),
                "color_source": color_meta["source"],
                "color_confidence": color_meta["confidence"],
                "sample_pixels": color_meta["pixels"],
                "path_count": len(face_paths),
            }
        )

    debug_svg_path = create_debug_region_svg(
        file_id,
        viewbox,
        faces,
        line_body,
    )

    final_svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{GEN_SIZE}" height="{GEN_SIZE}" viewBox="{min_x:g} {min_y:g} {vb_w:g} {vb_h:g}" xmlns="http://www.w3.org/2000/svg">
  <rect x="{min_x:g}" y="{min_y:g}" width="{vb_w:g}" height="{vb_h:g}" fill="white"/>
  <g id="auto-color-fills">
    {chr(10).join(fill_items)}
  </g>
  <g id="original-black-line-art">
    {line_body}
  </g>
</svg>
'''

    ok, err = validate_svg_string(final_svg)

    if not ok:
        broken_path = os.path.join(OUTPUT_DIR, f"{file_id}_colored_BROKEN.svg")
        with open(broken_path, "w", encoding="utf-8") as f:
            f.write(final_svg)

        raise ValueError(f"Generated SVG is invalid: {err}. Saved: {broken_path}")

    with open(final_svg_path, "w", encoding="utf-8") as f:
        f.write(final_svg)

    quality = {
        "file_id": file_id,
        "input_svg": svg_path,
        "bw_png": bw_path,
        "color_reference": color_path,
        "final_svg": final_svg_path,
        "debug_vector_faces_svg": debug_svg_path,
        "palette_debug_png": palette_path,
        "svg_path_count": topology["path_count"],
        "wall_geometry_count": topology["wall_geom_count"],
        "region_count": len(faces),
        "fill_path_count": len(fill_items),
        "selected_gap_close_px": selected_gap_px,
        "palette": [rgb_to_hex(c) for c in palette],
        "regions": region_meta,
    }

    quality_path = os.path.join(DEBUG_DIR, f"{file_id}_quality.json")

    with open(quality_path, "w", encoding="utf-8") as f:
        json.dump(quality, f, indent=2)

    print("[OK] Final colored SVG:", final_svg_path)
    print("[DEBUG] Vector faces:", debug_svg_path)
    print("[DEBUG] Palette:", palette_path)
    print("[DEBUG] Quality:", quality_path)
    print("[INFO] Regions:", len(faces))
    print("[INFO] Fill paths:", len(fill_items))
    print("[INFO] Gap close px:", selected_gap_px)

    return final_svg_path


# ============================================================
# Full Flow
# ============================================================

def colorize(file_id, prompt):
    generate_color_reference(file_id, prompt)
    return build_colored_svg(file_id)


# ============================================================
# Example Usage
# ============================================================

if __name__ == "__main__":
    prompt = input("Enter prompt: ").strip()

    file_id = generate_bw_and_svg(prompt)

    choice = input("Do you want to color it? (y/n): ").strip().lower()

    if choice == "y":
        final_svg = colorize(file_id, prompt)
        print("Done:", final_svg)
    else:
        print("Done.")