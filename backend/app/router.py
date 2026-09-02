from backend.app.tools.computer import open_application


APPLICATIONS = {
    "calculator": "Calculator",
    "safari": "Safari",
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "finder": "Finder",
    "terminal": "Terminal",
    "vscode": "Visual Studio Code",
    "vs code": "Visual Studio Code",
}


def route_command(command: str) -> dict:
    """
    Route a natural-language command to the appropriate LEO tool.
    """

    normalized_command = command.strip().lower()

    # ---------------------------------
    # Open application commands
    # ---------------------------------

    if normalized_command.startswith("open "):
        application = normalized_command[5:].strip()

        if application in APPLICATIONS:
            application_name = APPLICATIONS[application]

            result = open_application(application_name)

            return {
                **result,
                "command": command,
            }

    # ---------------------------------
    # Unknown command
    # ---------------------------------

    return {
        "success": True,
        "action": "unknown",
        "command": command,
        "message": f'LEO received: "{command}"',
        "status": "completed",
    }