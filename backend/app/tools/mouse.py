import pyautogui


def get_mouse_position() -> dict:
    """
    Return the current mouse cursor position.
    """

    try:
        x, y = pyautogui.position()

        return {
            "success": True,
            "action": "get_mouse_position",
            "x": x,
            "y": y,
            "message": f"Mouse position: ({x}, {y})",
        }

    except Exception as error:
        return {
            "success": False,
            "action": "get_mouse_position",
            "message": (
                f"Unable to get mouse position: {error}"
            ),
        }


def get_screen_size() -> dict:
    """
    Return the current screen dimensions.
    """

    try:
        width, height = pyautogui.size()

        return {
            "success": True,
            "action": "get_screen_size",
            "width": width,
            "height": height,
        }

    except Exception as error:
        return {
            "success": False,
            "action": "get_screen_size",
            "message": (
                f"Unable to get screen size: {error}"
            ),
        }


def is_valid_position(x: int, y: int) -> bool:
    """
    Check whether coordinates are inside the screen.
    """

    width, height = pyautogui.size()

    return (
        0 <= x < width
        and 0 <= y < height
    )


def move_mouse(
    x: int,
    y: int,
    duration: float = 0.3,
) -> dict:
    """
    Safely move the mouse cursor.
    """

    try:

        if not is_valid_position(x, y):
            return {
                "success": False,
                "action": "move_mouse",
                "x": x,
                "y": y,
                "message": (
                    "Target coordinates are outside "
                    "the current screen."
                ),
            }

        pyautogui.moveTo(
            x,
            y,
            duration=duration,
        )

        current_x, current_y = (
            pyautogui.position()
        )

        return {
            "success": True,
            "action": "move_mouse",
            "x": current_x,
            "y": current_y,
            "message": (
                f"Mouse moved to "
                f"({current_x}, {current_y})."
            ),
        }

    except Exception as error:
        return {
            "success": False,
            "action": "move_mouse",
            "x": x,
            "y": y,
            "message": (
                f"Unable to move mouse: {error}"
            ),
        }


def click_mouse(
    x: int | None = None,
    y: int | None = None,
    button: str = "left",
) -> dict:
    """
    Safely click the mouse.
    """

    try:

        if x is not None and y is not None:

            if not is_valid_position(x, y):
                return {
                    "success": False,
                    "action": "click_mouse",
                    "x": x,
                    "y": y,
                    "message": (
                        "Target coordinates are outside "
                        "the current screen."
                    ),
                }

            pyautogui.click(
                x=x,
                y=y,
                button=button,
            )

        else:

            pyautogui.click(
                button=button
            )

        current_x, current_y = (
            pyautogui.position()
        )

        return {
            "success": True,
            "action": "click_mouse",
            "x": current_x,
            "y": current_y,
            "button": button,
            "message": (
                f"Mouse clicked at "
                f"({current_x}, {current_y})."
            ),
        }

    except Exception as error:
        return {
            "success": False,
            "action": "click_mouse",
            "x": x,
            "y": y,
            "button": button,
            "message": (
                f"Unable to click mouse: {error}"
            ),
        }