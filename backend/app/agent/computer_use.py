import time

import pyautogui

from backend.app.tools.computer import take_screenshot
from backend.app.tools.mouse import move_mouse, click_mouse
from backend.app.ai.vision import VisionEngine
from backend.app.ai.ocr import OCREngine


class ComputerUse:
    """
    Computer-use layer for LEO.

    Connects:

    Screenshot
        ↓
    OCR / Vision
        ↓
    Element Location
        ↓
    Coordinate Conversion
        ↓
    Mouse Movement
        ↓
    Click
    """

    def __init__(self):

        self.vision = VisionEngine()

        self.ocr = OCREngine()

    def observe(
        self,
        delay: float = 0,
    ) -> dict:
        """
        Capture the current screen.

        delay:
        Number of seconds to wait before taking
        the screenshot.
        """

        try:

            if delay > 0:

                time.sleep(delay)

            result = take_screenshot()

            if not result.get("success"):

                return {
                    "success": False,
                    "action": "observe",
                    "message": result.get(
                        "message",
                        "Unable to capture screen.",
                    ),
                }

            return {
                "success": True,
                "action": "observe",
                "image_path": result["path"],
                "message": (
                    "Screen captured successfully."
                ),
            }

        except Exception as error:

            return {
                "success": False,
                "action": "observe",
                "message": str(error),
            }

    def _get_screen_size(
        self,
    ) -> dict:
        """
        Get the actual mouse-controllable
        screen size.

        This may be different from screenshot
        size on macOS Retina displays.
        """

        try:

            width, height = pyautogui.size()

            return {
                "success": True,
                "width": width,
                "height": height,
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error),
            }

    def _convert_coordinates(
        self,
        screenshot_x: int,
        screenshot_y: int,
        screenshot_width: int,
        screenshot_height: int,
    ) -> dict:
        """
        Convert screenshot coordinates into
        actual mouse coordinates.

        Automatically handles macOS Retina
        display scaling.
        """

        screen_result = self._get_screen_size()

        if not screen_result.get("success"):

            return {
                "success": False,
                "message": screen_result.get(
                    "error",
                    "Unable to get screen size.",
                ),
            }

        actual_width = screen_result["width"]

        actual_height = screen_result["height"]

        if (
            screenshot_width <= 0
            or screenshot_height <= 0
        ):

            return {
                "success": False,
                "message": (
                    "Invalid screenshot dimensions."
                ),
            }

        scale_x = (
            actual_width
            / screenshot_width
        )

        scale_y = (
            actual_height
            / screenshot_height
        )

        actual_x = round(
            screenshot_x * scale_x
        )

        actual_y = round(
            screenshot_y * scale_y
        )

        # Keep coordinates inside screen.

        actual_x = max(
            0,
            min(
                actual_x,
                actual_width - 1,
            ),
        )

        actual_y = max(
            0,
            min(
                actual_y,
                actual_height - 1,
            ),
        )

        return {
            "success": True,

            "screenshot_x": screenshot_x,
            "screenshot_y": screenshot_y,

            "mouse_x": actual_x,
            "mouse_y": actual_y,

            "screenshot_width": screenshot_width,
            "screenshot_height": screenshot_height,

            "screen_width": actual_width,
            "screen_height": actual_height,

            "scale_x": scale_x,
            "scale_y": scale_y,
        }

    def observe_and_find_text(
        self,
        target: str,
        delay: float = 0,
    ) -> dict:
        """
        Capture the screen and locate visible
        text using OCR.

        Useful for buttons, input fields,
        labels, menus, and other UI elements
        containing readable text.
        """

        observation = self.observe(
            delay=delay
        )

        if not observation.get("success"):

            return {
                "success": False,
                "action": "find_text",
                "target": target,
                "message": observation.get(
                    "message",
                    "Unable to observe screen.",
                ),
            }

        image_path = observation["image_path"]

        ocr_result = self.ocr.find_text(
            image_path=image_path,
            target=target,
        )

        if not ocr_result.get("success"):

            return {
                "success": False,
                "action": "find_text",
                "target": target,
                "message": ocr_result.get(
                    "error",
                    f"Could not find '{target}'.",
                ),
                "ocr_result": ocr_result,
            }

        if not ocr_result.get("found"):

            return {
                "success": False,
                "action": "find_text",
                "target": target,
                "message": (
                    f"Could not find text "
                    f"'{target}' on the screen."
                ),
                "ocr_result": ocr_result,
            }

        screenshot_x = ocr_result["x"]

        screenshot_y = ocr_result["y"]

        screenshot_width = ocr_result[
            "image_width"
        ]

        screenshot_height = ocr_result[
            "image_height"
        ]

        conversion = self._convert_coordinates(
            screenshot_x=screenshot_x,
            screenshot_y=screenshot_y,
            screenshot_width=screenshot_width,
            screenshot_height=screenshot_height,
        )

        if not conversion.get("success"):

            return {
                "success": False,
                "action": "find_text",
                "target": target,
                "message": conversion.get(
                    "message",
                    "Coordinate conversion failed.",
                ),
                "ocr_result": ocr_result,
            }

        return {
            "success": True,
            "action": "find_text",
            "target": target,

            # Actual mouse coordinates

            "x": conversion["mouse_x"],
            "y": conversion["mouse_y"],

            # Original screenshot coordinates

            "screenshot_x": screenshot_x,
            "screenshot_y": screenshot_y,

            "confidence": ocr_result.get(
                "confidence",
                0,
            ),

            "text": ocr_result.get(
                "text",
                target,
            ),

            "coordinate_conversion": conversion,

            "ocr_result": ocr_result,
        }

    def observe_and_locate(
        self,
        target: str,
        delay: float = 0,
    ) -> dict:
        """
        Capture the screen and locate a visible
        UI element using Vision.
        """

        observation = self.observe(
            delay=delay
        )

        if not observation.get("success"):

            return {
                "success": False,
                "action": "locate",
                "target": target,
                "message": observation.get(
                    "message",
                    "Unable to observe screen.",
                ),
            }

        image_path = observation["image_path"]

        vision_result = self.vision.locate_element(
            image_path=image_path,
            target=target,
        )

        if not vision_result.get("success"):

            return {
                "success": False,
                "action": "locate",
                "target": target,
                "message": vision_result.get(
                    "error",
                    "Vision analysis failed.",
                ),
                "vision_result": vision_result,
            }

        location = vision_result.get(
            "location",
            {},
        )

        if not location.get("found"):

            return {
                "success": False,
                "action": "locate",
                "target": target,
                "message": (
                    f"Could not find '{target}' "
                    "on the current screen."
                ),
                "vision_result": vision_result,
            }

        screenshot_x = location.get("x")

        screenshot_y = location.get("y")

        screenshot_width = vision_result.get(
            "screen_width"
        )

        screenshot_height = vision_result.get(
            "screen_height"
        )

        conversion = self._convert_coordinates(
            screenshot_x=screenshot_x,
            screenshot_y=screenshot_y,
            screenshot_width=screenshot_width,
            screenshot_height=screenshot_height,
        )

        if not conversion.get("success"):

            return {
                "success": False,
                "action": "locate",
                "target": target,
                "message": conversion.get(
                    "message",
                    "Coordinate conversion failed.",
                ),
                "vision_result": vision_result,
            }

        return {
            "success": True,

            "action": "locate",

            "target": target,

            # Actual mouse coordinates

            "x": conversion["mouse_x"],
            "y": conversion["mouse_y"],

            # Original screenshot coordinates

            "screenshot_x": screenshot_x,
            "screenshot_y": screenshot_y,

            "confidence": location.get(
                "confidence",
                0,
            ),

            "description": location.get(
                "description",
                target,
            ),

            "coordinate_conversion": conversion,

            "vision_result": vision_result,
        }

    def click_text(
        self,
        target: str,
        delay: float = 0,
    ) -> dict:
        """
        Find visible text using OCR and click it.
        """

        location_result = (
            self.observe_and_find_text(
                target=target,
                delay=delay,
            )
        )

        if not location_result.get("success"):

            return {
                "success": False,
                "action": "click_text",
                "target": target,
                "message": location_result.get(
                    "message",
                    "Unable to find text.",
                ),
                "location_result": location_result,
            }

        x = location_result["x"]

        y = location_result["y"]

        move_result = move_mouse(
            x,
            y,
        )

        if not move_result.get("success"):

            return {
                "success": False,
                "action": "click_text",
                "target": target,
                "message": (
                    "Unable to move mouse "
                    "to text."
                ),
                "move_result": move_result,
                "location_result": location_result,
            }

        time.sleep(0.5)

        click_result = click_mouse(
            x,
            y,
        )

        if not click_result.get("success"):

            return {
                "success": False,
                "action": "click_text",
                "target": target,
                "message": (
                    "Unable to click text."
                ),
                "click_result": click_result,
                "location_result": location_result,
            }

        return {
            "success": True,

            "action": "click_text",

            "target": target,

            "x": x,
            "y": y,

            "confidence": location_result.get(
                "confidence",
                0,
            ),

            "text": location_result.get(
                "text",
                target,
            ),

            "message": (
                f"Successfully clicked "
                f"text '{target}' "
                f"at ({x}, {y})."
            ),

            "location_result": location_result,

            "move_result": move_result,

            "click_result": click_result,
        }

    def click_element(
        self,
        target: str,
        delay: float = 0,
    ) -> dict:
        """
        Locate a visible UI element using Vision
        and click it.

        The target is described in human-readable
        language instead of coordinates.
        """

        location_result = self.observe_and_locate(
            target=target,
            delay=delay,
        )

        if not location_result.get("success"):

            return {
                "success": False,
                "action": "click_element",
                "target": target,
                "message": location_result.get(
                    "message",
                    "Unable to locate target.",
                ),
                "location_result": location_result,
            }

        x = location_result["x"]

        y = location_result["y"]

        move_result = move_mouse(
            x,
            y,
        )

        if not move_result.get("success"):

            return {
                "success": False,
                "action": "click_element",
                "target": target,
                "message": (
                    "Unable to move mouse "
                    "to target."
                ),
                "move_result": move_result,
                "location_result": location_result,
            }

        time.sleep(0.5)

        click_result = click_mouse(
            x,
            y,
        )

        if not click_result.get("success"):

            return {
                "success": False,
                "action": "click_element",
                "target": target,
                "message": (
                    "Unable to click target."
                ),
                "click_result": click_result,
                "location_result": location_result,
            }

        return {
            "success": True,

            "action": "click_element",

            "target": target,

            "x": x,
            "y": y,

            "confidence": location_result.get(
                "confidence",
                0,
            ),

            "description": location_result.get(
                "description",
                target,
            ),

            "message": (
                f"Successfully clicked "
                f"'{target}' at ({x}, {y})."
            ),

            "location_result": location_result,

            "move_result": move_result,

            "click_result": click_result,
        }