from pathlib import Path
import json
from datetime import datetime

import ollama
from PIL import Image


class VisionEngine:
    """
    Local visual perception engine for LEO.

    Uses a multimodal Ollama model to understand screenshots
    and locate visible UI elements.

    Localization uses two stages:

    Stage 1:
    Approximate location on the complete screen.

    Stage 2:
    Precise location inside a large crop around
    the approximate location.
    """

    def __init__(self, model: str = "gemma3:4b"):
        self.model = model

    def _clean_json(self, content: str) -> str:
        """
        Remove accidental markdown code fences.
        """

        content = content.strip()

        if content.startswith("```"):

            content = content.replace(
                "```json",
                "",
                1,
            )

            content = content.replace(
                "```",
                "",
            )

        return content.strip()

    def _get_image_size(
        self,
        image_path: Path,
    ) -> tuple:
        """
        Return image width and height.
        """

        with Image.open(image_path) as image:
            return image.size

    def _create_localization_image(
        self,
        image_path: Path,
        max_width: int = 1470,
    ) -> dict:
        """
        Create a resized image for vision processing.

        macOS Retina screenshots can be twice the size
        of the actual display. A resized image makes
        localization easier and faster.
        """

        image = Image.open(
            image_path
        ).convert("RGB")

        original_width, original_height = image.size

        if original_width > max_width:

            scale = max_width / original_width

            processed_width = max_width

            processed_height = round(
                original_height * scale
            )

            image = image.resize(
                (
                    processed_width,
                    processed_height,
                )
            )

        else:

            processed_width = original_width
            processed_height = original_height

        output_dir = (
            image_path.parent
            / "vision_processed"
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        output_path = (
            output_dir
            / f"vision_{timestamp}.png"
        )

        image.save(output_path)

        return {
            "success": True,

            "path": output_path,

            "original_width": original_width,
            "original_height": original_height,

            "processed_width": processed_width,
            "processed_height": processed_height,

            "scale_x": (
                original_width
                / processed_width
            ),

            "scale_y": (
                original_height
                / processed_height
            ),
        }

    def _create_crop(
        self,
        image_path: Path,
        left: int,
        top: int,
        right: int,
        bottom: int,
    ) -> Path:
        """
        Create a cropped image for precise
        second-stage localization.
        """

        image = Image.open(
            image_path
        ).convert("RGB")

        width, height = image.size

        # Keep crop inside image boundaries.
        left = max(
            0,
            min(left, width - 1),
        )

        top = max(
            0,
            min(top, height - 1),
        )

        right = max(
            left + 1,
            min(right, width),
        )

        bottom = max(
            top + 1,
            min(bottom, height),
        )

        crop = image.crop(
            (
                left,
                top,
                right,
                bottom,
            )
        )

        crop_dir = (
            image_path.parent
            / "vision_crops"
        )

        crop_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        crop_path = (
            crop_dir
            / f"crop_{timestamp}.png"
        )

        crop.save(crop_path)

        return crop_path

    def analyze_screen(
        self,
        image_path: str,
        prompt: str | None = None,
    ) -> dict:
        """
        Analyze a screenshot and return a semantic
        description.
        """

        path = Path(
            image_path
        ).expanduser().resolve()

        if not path.exists():

            return {
                "success": False,
                "action": "analyze_screen",
                "error": (
                    f"Image does not exist: {path}"
                ),
            }

        try:

            processed = (
                self._create_localization_image(
                    path
                )
            )

            processed_path = (
                processed["path"]
            )

        except Exception as error:

            return {
                "success": False,
                "action": "analyze_screen",
                "error": (
                    f"Unable to prepare image: {error}"
                ),
            }

        if prompt is None:

            prompt = """
You are the visual perception system of LEO,
a local desktop AI assistant.

Analyze this screenshot.

Describe only what is visibly present.

Focus on:

- applications
- windows
- browser pages
- buttons
- input fields
- menus
- dialogs
- important interactive elements

Keep the response concise and useful.
"""

        try:

            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [
                            str(processed_path)
                        ],
                    }
                ],
            )

            observation = (
                response.message.content.strip()
            )

            if not observation:

                return {
                    "success": False,
                    "action": "analyze_screen",
                    "image_path": str(path),
                    "error": (
                        "Vision model returned "
                        "an empty response."
                    ),
                }

            return {
                "success": True,
                "action": "analyze_screen",
                "model": self.model,

                "image_path": str(path),

                "processed_image_path": (
                    str(processed_path)
                ),

                "screen_width": (
                    processed["original_width"]
                ),

                "screen_height": (
                    processed["original_height"]
                ),

                "observation": observation,
            }

        except Exception as error:

            return {
                "success": False,
                "action": "analyze_screen",
                "model": self.model,
                "image_path": str(path),
                "error": str(error),
            }

    def _approximate_location(
        self,
        image_path: Path,
        target: str,
    ) -> dict:
        """
        First-stage localization.

        Find the approximate center of the target
        on the complete processed screen.

        The result does not need to be pixel-perfect.
        It is used to create a large crop for the
        second precise localization stage.
        """

        prompt = f"""
You are the first-stage visual localization
system of LEO.

Find this visible UI element:

"{target}"

Look carefully at the actual screenshot.

Return the approximate CENTER of the target.

Use normalized coordinates:

x = 0 means far left
x = 1000 means far right

y = 0 means very top
y = 1000 means very bottom

IMPORTANT:

- Look at the actual visible UI.
- Do not guess from the target name.
- Ignore browser tabs unless they are the target.
- Ignore the address bar unless it is the target.
- Return the approximate location of the actual
  visible element.

Return ONLY valid JSON.

Use exactly:

{{
    "found": true,
    "description": "short description",
    "x": 500,
    "y": 500,
    "confidence": 0.0
}}

If the target is not visible:

{{
    "found": false,
    "description": "target not visible",
    "x": null,
    "y": null,
    "confidence": 0.0
}}

Return JSON only.
"""

        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [
                        str(image_path)
                    ],
                }
            ],
        )

        content = self._clean_json(
            response.message.content
        )

        result = json.loads(content)

        if not result.get("found"):

            return result

        x = result.get("x")
        y = result.get("y")

        if x is None or y is None:

            raise ValueError(
                "Approximate location returned "
                "missing coordinates."
            )

        x = float(x)
        y = float(y)

        if not 0 <= x <= 1000:

            raise ValueError(
                "Approximate x is invalid."
            )

        if not 0 <= y <= 1000:

            raise ValueError(
                "Approximate y is invalid."
            )

        result["x"] = x
        result["y"] = y

        return result

    def _locate_inside_image(
        self,
        image_path: Path,
        target: str,
    ) -> dict:
        """
        Second-stage precise localization.

        The target should be inside this crop.
        Return the precise center of the target.
        """

        image = Image.open(
            image_path
        ).convert("RGB")

        width, height = image.size

        prompt = f"""
You are the precise visual localization
system of LEO.

Find this visible UI element:

"{target}"

This image is a cropped section of a computer
screen.

Return the CENTER of the actual visible target.

Use normalized coordinates:

x = 0 means far left
x = 1000 means far right

y = 0 means very top
y = 1000 means very bottom

IMPORTANT:

- Locate the actual visible element.
- Do not return the center of the image.
- Do not guess.
- Carefully inspect buttons, text fields,
  controls and interactive elements.
- Return found=true only when the target is
  actually visible in this crop.

Return ONLY valid JSON.

Use exactly:

{{
    "found": true,
    "description": "short description",
    "x": 500,
    "y": 500,
    "confidence": 0.0
}}

If not visible:

{{
    "found": false,
    "description": "target not visible",
    "x": null,
    "y": null,
    "confidence": 0.0
}}

Return JSON only.
"""

        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [
                        str(image_path)
                    ],
                }
            ],
        )

        content = self._clean_json(
            response.message.content
        )

        result = json.loads(content)

        if not result.get("found"):

            return result

        normalized_x = result.get("x")
        normalized_y = result.get("y")

        if (
            normalized_x is None
            or normalized_y is None
        ):
            raise ValueError(
                "Precise localization returned "
                "missing coordinates."
            )

        normalized_x = float(
            normalized_x
        )

        normalized_y = float(
            normalized_y
        )

        if not (
            0 <= normalized_x <= 1000
        ):
            raise ValueError(
                "Precise x is invalid."
            )

        if not (
            0 <= normalized_y <= 1000
        ):
            raise ValueError(
                "Precise y is invalid."
            )

        pixel_x = round(
            normalized_x
            / 1000
            * width
        )

        pixel_y = round(
            normalized_y
            / 1000
            * height
        )

        # Keep pixel coordinates inside crop.
        pixel_x = max(
            0,
            min(pixel_x, width - 1),
        )

        pixel_y = max(
            0,
            min(pixel_y, height - 1),
        )

        result["pixel_x"] = pixel_x
        result["pixel_y"] = pixel_y

        return result

    def locate_element(
        self,
        image_path: str,
        target: str,
    ) -> dict:
        """
        Locate a visible UI element.

        Stage 1:
        Approximate the target location on the
        complete screen.

        Stage 2:
        Create a large crop around that location.

        Stage 3:
        Precisely locate the target inside the crop.
        """

        path = Path(
            image_path
        ).expanduser().resolve()

        if not path.exists():

            return {
                "success": False,
                "action": "locate_element",
                "error": (
                    f"Image does not exist: {path}"
                ),
            }

        try:

            processed = (
                self._create_localization_image(
                    path
                )
            )

            processed_path = (
                processed["path"]
            )

            processed_width = (
                processed["processed_width"]
            )

            processed_height = (
                processed["processed_height"]
            )

            original_width = (
                processed["original_width"]
            )

            original_height = (
                processed["original_height"]
            )

        except Exception as error:

            return {
                "success": False,
                "action": "locate_element",
                "error": (
                    f"Unable to prepare image: {error}"
                ),
            }

        try:

            # ----------------------------------
            # STAGE 1
            # Approximate location on full screen
            # ----------------------------------

            approximate_result = (
                self._approximate_location(
                    image_path=processed_path,
                    target=target,
                )
            )

            if not approximate_result.get(
                "found"
            ):

                return {
                    "success": True,
                    "action": "locate_element",
                    "model": self.model,

                    "image_path": str(path),

                    "processed_image_path": (
                        str(processed_path)
                    ),

                    "screen_width": original_width,
                    "screen_height": original_height,

                    "target": target,

                    "location": approximate_result,
                }

            normalized_x = (
                approximate_result["x"]
            )

            normalized_y = (
                approximate_result["y"]
            )

            approximate_x = round(
                normalized_x
                / 1000
                * processed_width
            )

            approximate_y = round(
                normalized_y
                / 1000
                * processed_height
            )

            # ----------------------------------
            # STAGE 2
            # Create a large crop around target
            # ----------------------------------

            # Large crop: 60% screen width,
            # 45% screen height.
            #
            # This gives the precise model plenty
            # of surrounding context.

            crop_width = round(
                processed_width * 0.60
            )

            crop_height = round(
                processed_height * 0.45
            )

            half_width = crop_width // 2
            half_height = crop_height // 2

            crop_left = (
                approximate_x - half_width
            )

            crop_top = (
                approximate_y - half_height
            )

            crop_right = (
                approximate_x + half_width
            )

            crop_bottom = (
                approximate_y + half_height
            )

            # Shift crop if it exceeds image edges.

            if crop_left < 0:

                crop_right -= crop_left
                crop_left = 0

            if crop_top < 0:

                crop_bottom -= crop_top
                crop_top = 0

            if crop_right > processed_width:

                overflow = (
                    crop_right
                    - processed_width
                )

                crop_left -= overflow
                crop_right = processed_width

            if crop_bottom > processed_height:

                overflow = (
                    crop_bottom
                    - processed_height
                )

                crop_top -= overflow
                crop_bottom = processed_height

            crop_left = max(
                0,
                crop_left,
            )

            crop_top = max(
                0,
                crop_top,
            )

            crop_right = min(
                processed_width,
                crop_right,
            )

            crop_bottom = min(
                processed_height,
                crop_bottom,
            )

            crop_path = self._create_crop(
                image_path=processed_path,
                left=crop_left,
                top=crop_top,
                right=crop_right,
                bottom=crop_bottom,
            )

            # ----------------------------------
            # STAGE 3
            # Precise localization in crop
            # ----------------------------------

            precise_result = (
                self._locate_inside_image(
                    image_path=crop_path,
                    target=target,
                )
            )

            if not precise_result.get(
                "found"
            ):

                return {
                    "success": True,
                    "action": "locate_element",
                    "model": self.model,

                    "image_path": str(path),

                    "processed_image_path": (
                        str(processed_path)
                    ),

                    "crop_image_path": (
                        str(crop_path)
                    ),

                    "screen_width": original_width,
                    "screen_height": original_height,

                    "target": target,

                    "approximate_location": (
                        approximate_result
                    ),

                    "location": precise_result,
                }

            # Position inside processed screen.
            processed_x = (
                crop_left
                + precise_result["pixel_x"]
            )

            processed_y = (
                crop_top
                + precise_result["pixel_y"]
            )

            # ----------------------------------
            # Convert processed coordinates
            # back to original Retina screenshot
            # ----------------------------------

            original_x = round(
                processed_x
                * processed["scale_x"]
            )

            original_y = round(
                processed_y
                * processed["scale_y"]
            )

            original_x = max(
                0,
                min(
                    original_x,
                    original_width - 1,
                ),
            )

            original_y = max(
                0,
                min(
                    original_y,
                    original_height - 1,
                ),
            )

            precise_result["x"] = (
                original_x
            )

            precise_result["y"] = (
                original_y
            )

            precise_result["screenshot_x"] = (
                original_x
            )

            precise_result["screenshot_y"] = (
                original_y
            )

            precise_result["processed_x"] = (
                processed_x
            )

            precise_result["processed_y"] = (
                processed_y
            )

            return {
                "success": True,
                "action": "locate_element",
                "model": self.model,

                "image_path": str(path),

                "processed_image_path": (
                    str(processed_path)
                ),

                "crop_image_path": (
                    str(crop_path)
                ),

                "screen_width": original_width,
                "screen_height": original_height,

                "target": target,

                "approximate_location": (
                    approximate_result
                ),

                "location": precise_result,
            }

        except json.JSONDecodeError as error:

            return {
                "success": False,
                "action": "locate_element",

                "image_path": str(path),
                "target": target,

                "error": (
                    "Vision returned invalid JSON: "
                    f"{error}"
                ),
            }

        except Exception as error:

            return {
                "success": False,
                "action": "locate_element",

                "image_path": str(path),
                "target": target,

                "error": str(error),
            }