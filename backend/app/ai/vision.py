from pathlib import Path

import ollama


class VisionEngine:
    """
    Local visual perception engine for LEO.

    Uses a multimodal Ollama model to understand screenshots
    captured from the user's computer.
    """

    def __init__(self, model: str = "gemma3:4b"):
        self.model = model

    def analyze_screen(
        self,
        image_path: str,
        prompt: str | None = None,
    ) -> dict:
        """
        Analyze a screenshot and return a semantic description
        of the visible computer screen.
        """

        path = Path(image_path).expanduser().resolve()

        if not path.exists():
            return {
                "success": False,
                "action": "analyze_screen",
                "error": f"Image does not exist: {path}",
            }

        if not path.is_file():
            return {
                "success": False,
                "action": "analyze_screen",
                "error": f"Path is not a file: {path}",
            }

        if prompt is None:
            prompt = """
You are the visual perception system of LEO,
a local desktop AI assistant.

Analyze this screenshot of a computer screen.

Describe only what is visibly present.

Focus especially on:

- which applications or windows are visible
- the active application if it can be determined
- browser pages or websites
- important text
- buttons
- input fields
- menus
- dialogs
- notifications
- visible controls
- anything the user could potentially interact with

Do not claim something is visible unless you can actually
see evidence of it in the screenshot.

Keep the observation concise but useful for another AI agent
that may need to decide what action to perform next.
"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [str(path)],
                    }
                ],
            )

            observation = response.message.content.strip()

            if not observation:
                return {
                    "success": False,
                    "action": "analyze_screen",
                    "image_path": str(path),
                    "error": "Vision model returned an empty response.",
                }

            return {
                "success": True,
                "action": "analyze_screen",
                "model": self.model,
                "image_path": str(path),
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
