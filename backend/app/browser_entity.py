WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://github.com",
    "gmail": "https://mail.google.com",
    "chatgpt": "https://chatgpt.com",
    "linkedin": "https://www.linkedin.com",
}


def extract_website(command: str) -> dict:
    """
    Extract a website entity from a natural-language command.
    """

    normalized = command.strip().lower()

    # Remove punctuation
    normalized = normalized.replace(",", "")
    normalized = normalized.replace(".", "")
    normalized = normalized.replace("?", "")

    # Remove conversational phrases
    filler_words = [
        "please",
        "could you",
        "can you",
        "would you",
        "for me",
        "leo",
    ]

    for phrase in filler_words:
        normalized = normalized.replace(phrase, " ")

    normalized = " ".join(normalized.split())

    # Remove browser action words
    action_words = [
        "open",
        "launch",
        "start",
        "visit",
        "go to",
    ]

    for action in action_words:
        if normalized.startswith(action + " "):
            normalized = normalized[len(action):].strip()
            break

    # Remove optional words
    normalized = normalized.removeprefix("the ").strip()
    normalized = normalized.removeprefix("my ").strip()

    # Match website
    if normalized in WEBSITES:
        return {
            "entity_type": "WEBSITE",
            "entity": normalized,
            "url": WEBSITES[normalized],
            "confidence": 1.0,
        }

    return {
        "entity_type": None,
        "entity": None,
        "url": None,
        "confidence": 0.0,
    }