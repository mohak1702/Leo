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