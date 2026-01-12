from typing import Tuple


# Analyzes basic readability of a text block
def analyze_readability(text: str) -> dict:
    words = text.split()
    sentences = text.count('.') + 1

    avg_words_per_sentence = len(words) / sentences
    avg_word_length = sum(len(w) for w in words) / max(len(words), 1)

    # Determine readability level based on thresholds
    if avg_words_per_sentence < 12 and avg_word_length < 5:
        level = "easy"
    elif avg_words_per_sentence < 20:
        level = "medium"
    else:
        level = "hard"

    return {
        "level": level,
        "avg_words_per_sentence": round(avg_words_per_sentence, 2),
        "avg_word_length": round(avg_word_length, 2)
    }


# Rule based analysis on alt text
def analyze_alt_text(image: dict) -> dict:
    alt = (image.get("alt") or "").lower()

    # Missing alt text
    if alt == "":
        return {"issue": "missing_alt", "severity": "high"}
    # Alt text with no meaning
    if alt in ["image", "photo", "picture", "icon"]:
        return {"issue": "generic_alt", "severity": "medium"}
    # Alt text provides little information
    if len(alt.split()) < 3:
        return {"issue": "weak_alt", "severity": "low"}

    return {"issue": None, "severity": None}


# Rule based analysis on link text
def analyze_links(link: dict) -> dict:
    text = (link.get("text") or "").lower()

    # Common vague phrases that provide no context to screen reader users
    vague = ["klik hier", "lees meer", "meer", "hier", "link"]

    # Check if any vague term appears in the link text
    if any(v in text for v in vague):
        return {
            "issue": "vague_link_text",
            "severity": "medium"
        }

    return {"issue": None, "severity": None}


# Classifies links based on their role in the page structure
def classify_link(link: dict) -> Tuple[str, float]:
    text = (link.get("text") or "").lower()
    href = (link.get("href") or "").lower()

    # Navigation links
    if text in ["home", "contact", "over ons", "about", "services"]:
        return "navigation", 0.9

    # Action links
    if any(word in text for word in ["download", "bestel", "inschrijven", "apply", "order"]):
        return "action", 0.85

    # Links with no direction
    if href.startswith("#") or len(text.split()) <= 1:
        return "ambiguous", 0.6

    return "reference", 0.7


# Determines the functional role of an image based on alt text and ARIA role.
def classify_image(image: dict) -> Tuple[str, float]:
    alt = (image.get("alt") or "").strip()
    role = (image.get("role") or "").lower()

    # Ignore decorative images
    if role == "presentation" or alt == "":
        return "decorative", 0.9

    # Longer alt text could mean informative image
    if len(alt.split()) >= 5:
        return "informative", 0.8

    return "functional", 0.7


# Determines the purpose of a text block
def classify_text_block(block: dict) -> Tuple[str, float]:
    text = block.get("text", "").lower()

    # Instructions
    if any(word in text for word in ["stap", "hoe", "handleiding", "volg"]):
        return "instructional", 0.8

    # Legal or policy-related
    if any(word in text for word in ["voorwaarden", "privacy", "beleid"]):
        return "technical", 0.85

    # Marketing
    if any(word in text for word in ["voordelen", "waarom", "ontdek"]):
        return "marketing", 0.75

    return "informational", 0.7


# Adds semantic role and confidence scores to extracted elements
def enrich_elements(elements: dict) -> dict:
    enriched = {
        "links": [],
        "images": [],
        "text_blocks": []
    }

    for link in elements.get("links", []):
        role, confidence = classify_link(link)
        link["semantic_role"] = role
        link["confidence"] = confidence
        enriched["links"].append(link)

    for image in elements.get("images", []):
        role, confidence = classify_image(image)
        image["semantic_role"] = role
        image["confidence"] = confidence
        enriched["images"].append(image)

    for block in elements.get("text_blocks", []):
        role, confidence = classify_text_block(block)
        block["semantic_role"] = role
        block["confidence"] = confidence
        enriched["text_blocks"].append(block)

    return enriched
