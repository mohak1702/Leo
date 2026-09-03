APPLICATION_ENTITIES = {
    "calculator": "Calculator",
    "safari": "Safari",
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "finder": "Finder",
    "terminal": "Terminal",
    "vscode": "Visual Studio Code",
    "vs code": "Visual Studio Code",
}


def extract_application(command: str) -> dict:
    """
    Extract an application entity from a natural-language command.
    """

    normalized = command.strip().lower()

    # Remove common punctuation
    normalized = normalized.replace(",", "")
    normalized = normalized.replace(".", "")
    normalized = normalized.replace("?", "")

    # Remove common conversational phrases
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

    # Remove action words
    action_words = [
        "open",
        "launch",
        "start",
    ]

    for action in action_words:
        if normalized.startswith(action + " "):
            normalized = normalized[len(action):].strip()
            break

    # Remove optional words
    normalized = normalized.removeprefix("my ").strip()
    normalized = normalized.removeprefix("the ").strip()

    # Match application
    if normalized in APPLICATION_ENTITIES:
        return {
            "entity_type": "APPLICATION",
            "entity": APPLICATION_ENTITIES[normalized],
            "confidence": 1.0,
        }

    return {
        "entity_type": None,
        "entity": None,
        "confidence": 0.0,
    }
