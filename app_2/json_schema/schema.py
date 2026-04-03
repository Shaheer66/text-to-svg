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