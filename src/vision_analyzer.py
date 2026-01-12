def analyze_image_with_vision(image: dict, vision_description: str) -> dict:
    """
    Validates the quality of alt text by comparing it with an AI-generated
    vision description of the image.

    Args:
        image (dict): Image metadata including alt text and surrounding context
        vision_description (str): Semantic description generated

    Returns:
        dict: Evaluation result indicating whether an accessibility issue exists
    """
    alt_text = (image.get("alt") or "").lower()
    image.get("context", "")

    # Missing alt text
    if not alt_text:
        return {
            "issue": True,
            "reason": "Missing alt text",
            "suggestion": "Provide a meaningful description of the image."
        }

    # Alt text does not align with visual meaning
    if vision_description.lower() not in alt_text.lower():
        return {
            "issue": True,
            "reason": "Alt text does not match image meaning",
            "suggestion": "Update alt text to reflect the image content."
        }

    return {
        "issue": False,
        "reason": "Alt text matches image meaning"
    }
