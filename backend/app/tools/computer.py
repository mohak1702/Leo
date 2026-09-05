import subprocess
from pathlib import Path
from datetime import datetime


def open_application(application_name: str) -> dict:
    """Open a macOS application by name."""
    try:
        subprocess.run(
            ["open", "-a", application_name],
            check=True,
        )

        return {
            "success": True,
            "action": "open_application",
            "application": application_name,
            "message": f"{application_name} opened successfully.",
        }

    except subprocess.CalledProcessError:
        return {
            "success": False,
            "action": "open_application",
            "application": application_name,
            "message": f"Unable to open {application_name}.",
        }

def quit_application(application_name: str) -> dict:
    """Quit a running macOS application."""

    try:
        # First check whether the application is actually running.
        check_script = f'''
tell application "System Events"
    return exists process "{application_name}"
end tell
'''

        check_result = subprocess.run(
            ["osascript", "-e", check_script],
            capture_output=True,
            text=True,
            check=True,
        )

        is_running = check_result.stdout.strip().lower() == "true"

        if not is_running:
            return {
                "success": False,
                "action": "quit_application",
                "application": application_name,
                "message": (
                    f"{application_name} is not a running macOS application."
                ),
            }

        # Application exists and is running, so quit it.
        quit_script = f'''
tell application "{application_name}" to quit
'''

        subprocess.run(
            ["osascript", "-e", quit_script],
            capture_output=True,
            text=True,
            check=True,
        )

        return {
            "success": True,
            "action": "quit_application",
            "application": application_name,
            "message": f"{application_name} closed successfully.",
        }

    except subprocess.CalledProcessError as error:
        return {
            "success": False,
            "action": "quit_application",
            "application": application_name,
            "message": error.stderr.strip()
            or f"Unable to close {application_name}.",
        }

def hide_application(application_name: str) -> dict:
    """Hide a macOS application."""
    try:
        script = (
            f'tell application "System Events" '
            f'to set visible of process "{application_name}" to false'
        )

        subprocess.run(
            ["osascript", "-e", script],
            check=True,
        )

        return {
            "success": True,
            "action": "hide_application",
            "application": application_name,
            "message": f"{application_name} hidden successfully.",
        }

    except subprocess.CalledProcessError:
        return {
            "success": False,
            "action": "hide_application",
            "application": application_name,
            "message": f"Unable to hide {application_name}.",
        }
def take_screenshot() -> dict:
    """
    Capture the current macOS screen and save it as a PNG
    for LEO's computer-use perception pipeline.
    """

    try:
        project_root = Path(__file__).resolve().parents[2]

        screenshot_dir = project_root / "runtime" / "screenshots"
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        screenshot_path = screenshot_dir / f"leo_{timestamp}.png"

        result = subprocess.run(
            [
                "screencapture",
                "-x",
                str(screenshot_path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        if not screenshot_path.exists():
            return {
                "success": False,
                "action": "take_screenshot",
                "message": "Screenshot command completed but no image was created.",
            }

        return {
            "success": True,
            "action": "take_screenshot",
            "path": str(screenshot_path),
            "message": "Current screen captured successfully.",
        }

    except subprocess.CalledProcessError as error:
        return {
            "success": False,
            "action": "take_screenshot",
            "message": (
                error.stderr.strip()
                or "Unable to capture the screen."
            ),
        }

    except Exception as error:
        return {
            "success": False,
            "action": "take_screenshot",
            "message": f"Screenshot failed: {error}",
        }