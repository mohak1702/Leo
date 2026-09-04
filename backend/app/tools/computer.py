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