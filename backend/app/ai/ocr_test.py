from pathlib import Path

import pytesseract
from PIL import Image


def find_text(
    image_path: str,
    search_text: str,
):
    """
    Find text in an image using Tesseract OCR.
    """

    path = Path(image_path).expanduser().resolve()

    if not path.exists():
        print(f"Image not found: {path}")
        return

    image = Image.open(path)

    data = pytesseract.image_to_data(
        image,
        output_type=pytesseract.Output.DICT,
    )

    search_text = search_text.lower().strip()

    print()
    print("=" * 60)
    print("SEARCHING FOR:", search_text)
    print("=" * 60)

    found = False

    for index, text in enumerate(data["text"]):

        text = text.strip()

        if not text:
            continue

        if search_text in text.lower():

            left = data["left"][index]
            top = data["top"][index]
            width = data["width"][index]
            height = data["height"][index]

            center_x = left + width // 2
            center_y = top + height // 2

            print()
            print("FOUND TEXT:", text)
            print("Bounding box:")
            print(
                f"left={left}, "
                f"top={top}, "
                f"width={width}, "
                f"height={height}"
            )
            print(
                f"Center: ({center_x}, {center_y})"
            )

            found = True

    if not found:

        print()
        print("Text not found.")


if __name__ == "__main__":

    import sys

    if len(sys.argv) < 3:

        print(
            "Usage:"
        )

        print(
            "python -m backend.app.ai.ocr_test "
            "<image_path> <text>"
        )

        raise SystemExit(1)

    image_path = sys.argv[1]

    search_text = " ".join(
        sys.argv[2:]
    )

    find_text(
        image_path,
        search_text,
    )
