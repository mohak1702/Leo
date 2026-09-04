from backend.app.entity import extract_application
from backend.app.browser_entity import extract_website

OPEN_COMMANDS = [
    "open",
    "launch",
    "start",
    "visit",
    "go to",
]


QUIT_COMMANDS = [
    "close",
    "quit",
    "exit",
]


HIDE_COMMANDS = [
    "hide",
]


FILLER_WORDS = [
    "please",
    "could you",
    "can you",
    "would you",
    "for me",
    "leo",
]

CLOSE_TAB_COMMANDS = [
    "close tab",
    "close the tab",
    "close",
]


def clean_command(command: str) -> str:
    """
    Clean common conversational words from a command.
    """

    normalized = command.strip().lower()

    normalized = normalized.replace(",", "")
    normalized = normalized.replace(".", "")
    normalized = normalized.replace("?", "")

    if normalized.startswith("leo "):
        normalized = normalized[4:].strip()

    for phrase in FILLER_WORDS:
        normalized = normalized.replace(phrase, " ")

    normalized = " ".join(normalized.split())

    return normalized


def detect_intent(command: str) -> dict:
    """
    Detect the user's intent from a natural-language command.
    """

    normalized_command = clean_command(command)

    # ---------------------------------
    # OPEN / VISIT WEBSITE
    # ---------------------------------

    for action in OPEN_COMMANDS:

        if normalized_command.startswith(action + " "):

            website_data = extract_website(normalized_command)

            if website_data["entity"]:
                return {
                    "intent": "OPEN_WEBSITE",
                    "target": website_data["url"],
                    "entity": website_data["entity"],
                    "entity_type": website_data["entity_type"],
                    "confidence": website_data["confidence"],
                }

    # ---------------------------------
    # OPEN APPLICATION
    # ---------------------------------

    for action in OPEN_COMMANDS:

        if normalized_command.startswith(action + " "):

            entity_data = extract_application(normalized_command)

            if entity_data["entity"]:
                return {
                    "intent": "OPEN_APPLICATION",
                    "target": entity_data["entity"],
                    "entity": entity_data["entity"],
                    "entity_type": entity_data["entity_type"],
                    "confidence": entity_data["confidence"],
                }
        # CLOSE CHROME TAB
    for action in CLOSE_TAB_COMMANDS:
        if normalized_command.startswith(action + " "):
            search_term = normalized_command[len(action):].strip()

            if search_term:
                return {
                    "intent": "CLOSE_CHROME_TAB",
                    "target": search_term,
                    "entity": search_term,
                    "entity_type": "BROWSER_TAB",
                    "confidence": 1.0,
                }

    # ---------------------------------
    # QUIT APPLICATION
    # ---------------------------------

    for action in QUIT_COMMANDS:

        if normalized_command.startswith(action + " "):

            entity_data = extract_application(
                "open " + normalized_command[len(action):].strip()
            )

            if entity_data["entity"]:
                return {
                    "intent": "QUIT_APPLICATION",
                    "target": entity_data["entity"],
                    "entity": entity_data["entity"],
                    "entity_type": entity_data["entity_type"],
                    "confidence": entity_data["confidence"],
                }

    # ---------------------------------
    # HIDE APPLICATION
    # ---------------------------------

    for action in HIDE_COMMANDS:

        if normalized_command.startswith(action + " "):

            entity_data = extract_application(
                "open " + normalized_command[len(action):].strip()
            )

            if entity_data["entity"]:
                return {
                    "intent": "HIDE_APPLICATION",
                    "target": entity_data["entity"],
                    "entity": entity_data["entity"],
                    "entity_type": entity_data["entity_type"],
                    "confidence": entity_data["confidence"],
                }

    # ---------------------------------
    # UNKNOWN
    # ---------------------------------

    return {
        "intent": "UNKNOWN",
        "target": None,
        "entity": None,
        "entity_type": None,
        "confidence": 0.0,
    }