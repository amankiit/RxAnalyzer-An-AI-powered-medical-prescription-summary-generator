from __future__ import annotations

BASE_PROMPT = """
You are a clinical documentation assistant. Extract prescription details from the provided
image and/or text. Return ONLY valid JSON that matches the provided JSON schema.

Rules:
- Do not guess. If a field is missing or unclear, use an empty string or an empty array.
- Keep medication names and SIGs as written; do not expand abbreviations unless explicit.
- The summary must be 1-3 concise clinical sentences and must not add new facts.
- The transcription should be verbatim from the image/text and may include line breaks.
""".strip()


def build_user_prompt(raw_text: str | None) -> str:
    if raw_text and raw_text.strip():
        return (
            "Use the following transcription as the source of truth. "
            "Do not infer information not present in the text.\n\n"
            f"TRANSCRIPTION:\n{raw_text.strip()}"
        )

    return (
        "Extract details from the attached prescription image. "
        "If you cannot read a value, leave it empty."
    )


PRESCRIPTION_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "transcription": {
            "type": "string",
            "description": "Verbatim transcription of the prescription text.",
        },
        "patient": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "dob": {"type": "string"},
            },
            "required": ["name", "dob"],
            "additionalProperties": False,
        },
        "prescriber": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "npi": {"type": "string"},
                "phone": {"type": "string"},
            },
            "required": ["name", "npi", "phone"],
            "additionalProperties": False,
        },
        "dates": {
            "type": "object",
            "properties": {
                "primary": {"type": "string"},
                "all": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["primary", "all"],
            "additionalProperties": False,
        },
        "medications": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "strength": {"type": "string"},
                    "form": {"type": "string"},
                    "sig": {"type": "string"},
                    "quantity": {"type": "string"},
                    "refills": {"type": "string"},
                    "notes": {"type": "string"},
                },
                "required": [
                    "name",
                    "strength",
                    "form",
                    "sig",
                    "quantity",
                    "refills",
                    "notes",
                ],
                "additionalProperties": False,
            },
        },
        "summary": {"type": "string"},
        "confidence": {
            "type": "object",
            "properties": {
                "overall": {"type": "number", "minimum": 0, "maximum": 1},
                "notes": {"type": "string"},
            },
            "required": ["overall", "notes"],
            "additionalProperties": False,
        },
    },
    "required": [
        "transcription",
        "patient",
        "prescriber",
        "dates",
        "medications",
        "summary",
        "confidence",
    ],
    "additionalProperties": False,
}
