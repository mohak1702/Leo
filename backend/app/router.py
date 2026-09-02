from backend.app.intent import detect_intent
from backend.app.tools.computer import open_application


def route_command(command: str) -> dict:
    """
    Route a command based on the detected intent.
    """

    intent_data = detect_intent(command)

    intent = intent_data["intent"]
    target = intent_data["target"]

    # ---------------------------------
    # OPEN APPLICATION
    # ---------------------------------

    if intent == "OPEN_APPLICATION":
        result = open_application(target)

        return {
            **result,
            "command": command,
            "intent": intent,
            "confidence": intent_data["confidence"],
        }

    # ---------------------------------
    # UNKNOWN COMMAND
    # ---------------------------------

    return {
        "success": True,
        "action": "unknown",
        "command": command,
        "intent": intent,
        "confidence": intent_data["confidence"],
        "message": f'LEO received: "{command}"',
        "status": "completed",
    }