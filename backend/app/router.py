from backend.app.intent import detect_intent
from backend.app.tools.computer import (
    open_application,
    quit_application,
    hide_application,
)


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
            "entity": target,
            "confidence": intent_data["confidence"],
            "status": "completed",
        }

    # ---------------------------------
    # QUIT APPLICATION
    # ---------------------------------

    if intent == "QUIT_APPLICATION":
        result = quit_application(target)

        return {
            **result,
            "command": command,
            "intent": intent,
            "entity": target,
            "confidence": intent_data["confidence"],
            "status": "completed",
        }

    # ---------------------------------
    # HIDE APPLICATION
    # ---------------------------------

    if intent == "HIDE_APPLICATION":
        result = hide_application(target)

        return {
            **result,
            "command": command,
            "intent": intent,
            "entity": target,
            "confidence": intent_data["confidence"],
            "status": "completed",
        }

    # ---------------------------------
    # UNKNOWN COMMAND
    # ---------------------------------

    return {
        "success": True,
        "action": "unknown",
        "command": command,
        "intent": intent,
        "entity": None,
        "confidence": intent_data["confidence"],
        "message": f'LEO received: "{command}"',
        "status": "completed",
    }