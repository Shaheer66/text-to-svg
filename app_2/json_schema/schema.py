"""
this folder have all of the schema to minimize the entropy and make consistency in the results of the model 
and also to make it easier to update the schema in one place if needed
"""
schema_v1 = {
    "type": "object",
    "properties": {
        "canvas": {
            "type": "string"
        },
        "stroke": {
            "type": "number"
        },
        "elements": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string"
                    },
                    "cx": {
                        "type": ["number", "null"]
                    },
                    "cy": {
                        "type": ["number", "null"]
                    },
                    "r": {
                        "type": ["number", "null"]
                    },
                    "x1": {
                        "type": ["number", "null"]
                    },
                    "y1": {
                        "type": ["number", "null"]
                    },
                    "x2": {
                        "type": ["number", "null"]
                    },
                    "y2": {
                        "type": ["number", "null"]
                    }
                },
                "required": [
                    "type",
                    "cx",
                    "cy",
                    "r",
                    "x1",
                    "y1",
                    "x2",
                    "y2"
                ],
                "additionalProperties": False
            }
        }
    },
    "required": ["canvas", "stroke", "elements"],
    "additionalProperties": False
}

schema_v2 = {
  "type": "object",
  "properties": {
    "viewBox": {
      "type": "string",
      "description": "Standard scalable canvas size, e.g., '0 0 24 24' or '0 0 512 512'"
    },
    "defs": {
      "type": ["array", "null"],
      "description": "Used for high-end icons: gradients, masks, and reusable filters.",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "type": { "type": "string", "enum": ["linearGradient", "radialGradient"] },
          "stops": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "offset": { "type": ["string", "number"] },
                "stopColor": { "type": "string" },
                "stopOpacity": { "type": "number" }
              },
              "required": ["offset", "stopColor"],
              "additionalProperties": False
            }
          },
          "x1": { "type": "string" }, "y1": { "type": "string" },
          "x2": { "type": "string" }, "y2": { "type": "string" },
          "cx": { "type": "string" }, "cy": { "type": "string" },
          "r": { "type": "string" }
        },
        "required": ["id", "type", "stops"],
        "additionalProperties": False
      }
    },
    "elements": {
      "type": "array",
      "items": { "$ref": "#/$defs/svgNode" }
    }
  },
  "required": ["viewBox", "elements"],
  "additionalProperties": False,
  "$defs": {
    "baseStyle": {
      "type": "object",
      "properties": {
        "fill": { "type": ["string", "null"] },
        "stroke": { "type": ["string", "null"] },
        "strokeWidth": { "type": ["number", "null"] },
        "strokeLinecap": { "type": ["string", "null"], "enum": ["butt", "round", "square", "null"] },
        "strokeLinejoin": { "type": ["string", "null"], "enum": ["miter", "round", "bevel", "null"] },
        "opacity": { "type": ["number", "null"] },
        "transform": { "type": ["string", "null"], "description": "e.g., 'rotate(45 12 12)' or 'translate(10,0)'" }
      }
    },
    "svgNode": {
      "allOf": [
        { "$ref": "#/$defs/baseStyle" },
        {
          "anyOf": [
            {
              "title": "Path",
              "type": "object",
              "properties": {
                "type": { "const": "path" },
                "d": { "type": "string" }
              },
              "required": ["type", "d"]
            },
            {
              "title": "Rectangle",
              "type": "object",
              "properties": {
                "type": { "const": "rect" },
                "x": { "type": "number" },
                "y": { "type": "number" },
                "width": { "type": "number" },
                "height": { "type": "number" },
                "rx": { "type": ["number", "null"] },
                "ry": { "type": ["number", "null"] }
              },
              "required": ["type", "x", "y", "width", "height"]
            },
            {
              "title": "Circle",
              "type": "object",
              "properties": {
                "type": { "const": "circle" },
                "cx": { "type": "number" },
                "cy": { "type": "number" },
                "r": { "type": "number" }
              },
              "required": ["type", "cx", "cy", "r"]
            },
            {
              "title": "Line",
              "type": "object",
              "properties": {
                "type": { "const": "line" },
                "x1": { "type": "number" },
                "y1": { "type": "number" },
                "x2": { "type": "number" },
                "y2": { "type": "number" }
              },
              "required": ["type", "x1", "y1", "x2", "y2"]
            },
            {
              "title": "Polygon/Polyline",
              "type": "object",
              "properties": {
                "type": { "type": "string", "enum": ["polygon", "polyline"] },
                "points": { "type": "string" }
              },
              "required": ["type", "points"]
            },
            {
              "title": "Group",
              "type": "object",
              "properties": {
                "type": { "const": "g" },
                "children": {
                  "type": "array",
                  "items": { "$ref": "#/$defs/svgNode" }
                }
              },
              "required": ["type", "children"],
              "additionalProperties": False
            }
          ]
        }
      ]
    }
  }
}

schema_v3 = {
    "type": "object",
    "properties": {
        "viewBox": {
            "type": "string",
            "description": "Standard scalable canvas size, e.g., '0 0 24 24' or '0 0 512 512'"
        },
        "defs": {
            "type": ["array", "null"],
            "description": "Used for high-end icons: gradients, masks, and reusable filters.",
            "items": {
                "type": "object",
                "properties": {
                    "id": { "type": "string" },
                    "type": { "type": "string", "enum": ["linearGradient", "radialGradient"] },
                    "stops": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "offset": { "type": ["string", "number"] },
                                "stopColor": { "type": "string" },
                                "stopOpacity": { "type": "number" }
                            },
                            "required": ["offset", "stopColor", "stopOpacity"],
                            "additionalProperties": False
                        }
                    },
                    "x1": { "type": "string" }, "y1": { "type": "string" },
                    "x2": { "type": "string" }, "y2": { "type": "string" },
                    "cx": { "type": "string" }, "cy": { "type": "string" },
                    "r": { "type": "string" }
                },
                "required": ["id", "type", "stops"],
                "additionalProperties": False
            }
        },
        "elements": {
            "type": "array",
            "items": { "$ref": "#/$defs/svgNode" }
        }
    },
    "required": ["viewBox", "elements"],
    "additionalProperties": False,
    "$defs": {
        "baseStyle": {
            "type": "object",
            "properties": {
                "fill": { "type": "string" },
                "stroke": { "type": "string" },
                "strokeWidth": { "type": "number" },
                "strokeLinecap": { "type": "string", "enum": ["butt", "round", "square"] },
                "strokeLinejoin": { "type": "string", "enum": ["miter", "round", "bevel"] },
                "opacity": { "type": "number" },
                "transform": { "type": "string", "description": "e.g., 'rotate(45 12 12)'" }
            },
            "additionalProperties": False
        },
        "svgNode": {
            "type": "object",
            "properties": {
                "type": { "type": "string", "enum": ["path", "rect", "circle", "line", "polygon", "polyline", "g"] },
                "d": { "type": "string" },
                "x": { "type": "number" },
                "y": { "type": "number" },
                "width": { "type": "number" },
                "height": { "type": "number" },
                "rx": { "type": "number" },
                "ry": { "type": "number" },
                "cx": { "type": "number" },
                "cy": { "type": "number" },
                "r": { "type": "number" },
                "x1": { "type": "number" },
                "y1": { "type": "number" },
                "x2": { "type": "number" },
                "y2": { "type": "number" },
                "points": { "type": "string" },
                "children": {
                    "type": "array",
                    "items": { "$ref": "#/$defs/svgNode" }
                },
                # Style properties flattened for better Strict Mode compatibility
                "fill": { "type": "string" },
                "stroke": { "type": "string" },
                "strokeWidth": { "type": "number" },
                "strokeLinecap": { "type": "string", "enum": ["butt", "round", "square"] },
                "strokeLinejoin": { "type": "string", "enum": ["miter", "round", "bevel"] },
                "opacity": { "type": "number" },
                "transform": { "type": "string" }
            },
            # Azure Strict Mode: ALL properties above MUST be in this list.
            "required": [
                "type", "d", "x", "y", "width", "height", 
                "cx", "cy", "r", "fill", "stroke", "strokeWidth", "children"
            ],
            "additionalProperties": False
        }
    }
}