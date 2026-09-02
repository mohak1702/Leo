APPLICATIONS = {
    "calculator": "Calculator",
    "safari": "Safari",
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "finder": "Finder",
    "terminal": "Terminal",
    "vscode": "Visual Studio Code",
    "vs code": "Visual Studio Code",
}


OPEN_COMMANDS = [
    "open",
    "launch",
    "start",
]


FILLER_WORDS = [
    "please",
    "could you",
    "can you",
    "would you",
    "for me",
    "leo",
]


def clean_command(command: str) -> str:
    """
    Clean common conversational words from a command.
    """

    normalized = command.strip().lower()

    # Remove common punctuation
    normalized = normalized.replace(",", "")
    normalized = normalized.replace(".", "")
    normalized = normalized.replace("?", "")

    # Remove LEO wake name
    if normalized.startswith("leo "):
        normalized = normalized[4:].strip()

    # Remove conversational phrases
    for phrase in FILLER_WORDS:
        normalized = normalized.replace(phrase, " ")

    # Normalize whitespace
    normalized = " ".join(normalized.split())

    return normalized


def detect_intent(command: str) -> dict:
    """
    Detect the user's intent from a natural-language command.
    """

    normalized_command = clean_command(command)

    # Check application commands
    for action in OPEN_COMMANDS:

        prefix = action + " "

        if normalized_command.startswith(prefix):

            target = normalized_command[len(prefix):].strip()

            # Direct application match
            if target in APPLICATIONS:
                return {
                    "intent": "OPEN_APPLICATION",
                    "target": APPLICATIONS[target],
                    "confidence": 1.0,
                }

            # Handle phrases such as:
            # "open my terminal"
            # "open the calculator"
            target = target.removeprefix("my ").strip()
            target = target.removeprefix("the ").strip()

            if target in APPLICATIONS:
                return {
                    "intent": "OPEN_APPLICATION",
                    "target": APPLICATIONS[target],
                    "confidence": 0.95,
                }

    return {
        "intent": "UNKNOWN",
        "target": None,
        "confidence": 0.0,
    }