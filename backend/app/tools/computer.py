import subprocess


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
    """Quit a macOS application."""
    try:
        script = f'tell application "{application_name}" to quit'

        subprocess.run(
            ["osascript", "-e", script],
            check=True,
        )

        return {
            "success": True,
            "action": "quit_application",
            "application": application_name,
            "message": f"{application_name} closed successfully.",
        }

    except subprocess.CalledProcessError:
        return {
            "success": False,
            "action": "quit_application",
            "application": application_name,
            "message": f"Unable to close {application_name}.",
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