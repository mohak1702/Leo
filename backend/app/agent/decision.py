from backend.app.intent import detect_intent


def decide(command: str) -> dict:
    """
    Decide which registered tool should handle a command.

    This is the temporary local decision layer.
    It will later be replaced or enhanced by an LLM.
    """

    intent_data = detect_intent(command)

    intent = intent_data["intent"]
    target = intent_data["target"]

    tool_map = {
        "OPEN_APPLICATION": "open_application",
        "QUIT_APPLICATION": "quit_application",
        "HIDE_APPLICATION": "hide_application",
        "OPEN_WEBSITE": "open_url",
        "CLOSE_CHROME_TAB": "close_chrome_tab",
    }

    tool_name = tool_map.get(intent)

    if tool_name is None:
        return {
            "success": False,
            "tool": None,
            "arguments": {},
            "reason": "No suitable tool found.",
        }

    if intent == "OPEN_APPLICATION":
        arguments = {
            "application_name": target,
        }

    elif intent == "QUIT_APPLICATION":
        arguments = {
            "application_name": target,
        }

    elif intent == "HIDE_APPLICATION":
        arguments = {
            "application_name": target,
        }

    elif intent == "OPEN_WEBSITE":
        arguments = {
            "url": target,
        }

    elif intent == "CLOSE_CHROME_TAB":
        arguments = {
            "search_term": target,
        }

    else:
        arguments = {}

    return {
        "success": True,
        "tool": tool_name,
        "arguments": arguments,
        "reason": f"Selected {tool_name}.",
    }
