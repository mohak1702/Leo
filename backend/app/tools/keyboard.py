import pyautogui


def type_text(text: str, interval: float = 0.03) -> dict:
    """
    Type text using the keyboard.
    """

    try:
        pyautogui.write(
            text,
            interval=interval,
        )

        return {
            "success": True,
            "action": "type_text",
            "text": text,
            "message": f"Typed text: {text}",
        }

    except Exception as error:
        return {
            "success": False,
            "action": "type_text",
            "text": text,
            "message": f"Unable to type text: {error}",
        }


def press_key(key: str, presses: int = 1) -> dict:
    """
    Press a keyboard key.
    """

    try:
        pyautogui.press(
            key,
            presses=presses,
        )

        return {
            "success": True,
            "action": "press_key",
            "key": key,
            "presses": presses,
            "message": f"Pressed key: {key}",
        }

    except Exception as error:
        return {
            "success": False,
            "action": "press_key",
            "key": key,
            "message": f"Unable to press key: {error}",
        }


def press_hotkey(*keys: str) -> dict:
    """
    Press a keyboard shortcut.

    Example:
    press_hotkey("command", "c")
    """

    try:
        pyautogui.hotkey(*keys)

        return {
            "success": True,
            "action": "press_hotkey",
            "keys": list(keys),
            "message": f"Pressed shortcut: {' + '.join(keys)}",
        }

    except Exception as error:
        return {
            "success": False,
            "action": "press_hotkey",
            "keys": list(keys),
            "message": f"Unable to press shortcut: {error}",
        }
