from pathlib import Path
import re

import pytesseract
from PIL import Image


class OCREngine:
    """
    OCR engine for LEO.

    Uses Tesseract to detect visible text
    and return exact bounding boxes.
    """

    def _get_image_data(
        self,
        image_path: Path,
    ) -> dict:
        """
        Extract OCR data from an image.
        """

        image = Image.open(
            image_path
        ).convert("RGB")

        data = pytesseract.image_to_data(
            image,
            output_type=pytesseract.Output.DICT,
        )

        return data

    def _normalize_text(
        self,
        text: str,
    ) -> str:
        """
        Normalize OCR text.

        Example:

        '"Search",' -> 'search'
        'SEARCH' -> 'search'
        """

        text = text.strip().lower()

        text = re.sub(
            r"[^a-z0-9\s]",
            "",
            text,
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    def find_text(
        self,
        image_path: str,
        target: str,
    ) -> dict:
        """
        Find visible text inside an image.

        Returns the center coordinates of
        the matching text.
        """

        path = Path(
            image_path
        ).expanduser().resolve()

        if not path.exists():

            return {
                "success": False,
                "action": "find_text",
                "error": (
                    f"Image does not exist: {path}"
                ),
            }

        target = target.strip()

        if not target:

            return {
                "success": False,
                "action": "find_text",
                "error": "Target text is empty.",
            }

        try:

            data = self._get_image_data(
                path
            )

            matches = []

            normalized_target = (
                self._normalize_text(target)
            )

            if not normalized_target:

                return {
                    "success": False,
                    "action": "find_text",
                    "error": (
                        "Target text is invalid."
                    ),
                }

            for index, text in enumerate(
                data["text"]
            ):

                original_text = text.strip()

                if not original_text:
                    continue

                normalized_text = (
                    self._normalize_text(
                        original_text
                    )
                )

                if not normalized_text:
                    continue

                # Ignore extremely short OCR noise.
                if (
                    len(normalized_text) < 2
                    and len(normalized_target) > 2
                ):
                    continue

                match_type = None

                # Best match:
                # Search == Search
                if (
                    normalized_text
                    == normalized_target
                ):

                    match_type = "exact"

                # Partial match:
                # SearchVideos contains Search
                elif (
                    len(normalized_target) >= 3
                    and normalized_target
                    in normalized_text
                ):

                    match_type = "contains_target"

                # Reverse partial match:
                # Search is contained inside a
                # meaningful target phrase.
                elif (
                    len(normalized_text) >= 3
                    and normalized_text
                    in normalized_target
                ):

                    match_type = "contained_in_target"

                # Do not add invalid matches.
                if not match_type:
                    continue

                left = int(
                    data["left"][index]
                )

                top = int(
                    data["top"][index]
                )

                width = int(
                    data["width"][index]
                )

                height = int(
                    data["height"][index]
                )

                confidence = (
                    data["conf"][index]
                )

                try:

                    confidence = float(
                        confidence
                    )

                except (
                    ValueError,
                    TypeError,
                ):

                    confidence = 0.0

                center_x = (
                    left
                    + width // 2
                )

                center_y = (
                    top
                    + height // 2
                )

                # Exact matches get priority.
                if match_type == "exact":

                    priority = 3

                elif (
                    match_type
                    == "contains_target"
                ):

                    priority = 2

                else:

                    priority = 1

                matches.append(
                    {
                        "text": original_text,

                        "normalized_text": (
                            normalized_text
                        ),

                        "match_type": match_type,

                        "priority": priority,

                        "left": left,
                        "top": top,

                        "width": width,
                        "height": height,

                        "center_x": center_x,
                        "center_y": center_y,

                        "confidence": confidence,
                    }
                )

            if not matches:

                return {
                    "success": True,
                    "action": "find_text",

                    "image_path": str(path),

                    "target": target,

                    "found": False,

                    "matches": [],
                }

            # Sort by:
            #
            # 1. Match priority
            # 2. OCR confidence

            matches.sort(
                key=lambda item: (
                    item["priority"],
                    item["confidence"],
                ),
                reverse=True,
            )

            best_match = matches[0]

            image = Image.open(path)

            image_width, image_height = (
                image.size
            )

            return {
                "success": True,

                "action": "find_text",

                "image_path": str(path),

                "target": target,

                "found": True,

                "text": (
                    best_match["text"]
                ),

                "normalized_text": (
                    best_match[
                        "normalized_text"
                    ]
                ),

                "match_type": (
                    best_match[
                        "match_type"
                    ]
                ),

                "x": (
                    best_match["center_x"]
                ),

                "y": (
                    best_match["center_y"]
                ),

                "confidence": (
                    best_match["confidence"]
                ),

                "image_width": image_width,

                "image_height": image_height,

                "bounding_box": {
                    "left": (
                        best_match["left"]
                    ),

                    "top": (
                        best_match["top"]
                    ),

                    "width": (
                        best_match["width"]
                    ),

                    "height": (
                        best_match["height"]
                    ),
                },

                "matches": matches,
            }

        except Exception as error:

            return {
                "success": False,

                "action": "find_text",

                "image_path": str(path),

                "target": target,

                "error": str(error),
            }