import subprocess
import webbrowser


def open_url(url: str) -> dict:
    """
    Open a URL using the default macOS browser.
    """

    try:
        webbrowser.open(url)

        return {
            "success": True,
            "action": "open_url",
            "url": url,
            "message": f"Opened {url} successfully.",
        }

    except Exception:
        return {
            "success": False,
            "action": "open_url",
            "url": url,
            "message": f"Unable to open {url}.",
        }
def get_safari_tabs() -> dict:
    """
    Get the names and URLs of all open Safari tabs.
    """

    script = '''
tell application "Safari"
    set tabData to {}

    repeat with w in windows
        repeat with t in tabs of w
            set tabName to name of t
            set tabURL to URL of t

            set end of tabData to tabName & " | " & tabURL
        end repeat
    end repeat

    return tabData
end tell
'''

    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=True,
        )

        tabs = result.stdout.strip()

        return {
            "success": True,
            "action": "get_safari_tabs",
            "tabs": tabs.split(", "),
            "message": "Safari tabs retrieved successfully.",
        }

    except subprocess.CalledProcessError as error:
        return {
            "success": False,
            "action": "get_safari_tabs",
            "tabs": [],
            "message": error.stderr.strip() or "Unable to retrieve Safari tabs.",
        }
def close_safari_tab(search_term: str) -> dict:
    """
    Close the first Safari tab whose name or URL contains search_term.
    """

    script = f'''
tell application "Safari"
    repeat with w in windows
        repeat with t in tabs of w
            set tabName to name of t
            set tabURL to URL of t

            if tabName contains "{search_term}" or tabURL contains "{search_term}" then
                close t
                return "closed"
            end if
        end repeat
    end repeat

    return "not_found"
end tell
'''

    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=True,
        )

        result_text = result.stdout.strip()

        if result_text == "closed":
            return {
                "success": True,
                "action": "close_safari_tab",
                "target": search_term,
                "message": f"Safari tab matching '{search_term}' closed successfully.",
            }

        return {
            "success": False,
            "action": "close_safari_tab",
            "target": search_term,
            "message": f"No Safari tab matching '{search_term}' was found.",
        }

    except subprocess.CalledProcessError as error:
        return {
            "success": False,
            "action": "close_safari_tab",
            "target": search_term,
            "message": error.stderr.strip() or "Unable to close Safari tab.",
        }
def get_chrome_tabs() -> dict:
    """
    Get the names and URLs of all open Google Chrome tabs.
    """

    script = '''
tell application "Google Chrome"
    set tabData to {}

    repeat with w in windows
        repeat with t in tabs of w
            set tabName to title of t
            set tabURL to URL of t

            set end of tabData to tabName & " | " & tabURL
        end repeat
    end repeat

    return tabData
end tell
'''

    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=True,
        )

        tabs = result.stdout.strip()

        return {
            "success": True,
            "action": "get_chrome_tabs",
            "tabs": tabs.split(", "),
            "message": "Chrome tabs retrieved successfully.",
        }

    except subprocess.CalledProcessError as error:
        return {
            "success": False,
            "action": "get_chrome_tabs",
            "tabs": [],
            "message": error.stderr.strip()
            or "Unable to retrieve Chrome tabs.",
        }
def close_chrome_tab(search_term: str) -> dict:
    """
    Close the first Chrome tab whose title or URL contains search_term.
    """

    script = f'''
tell application "Google Chrome"
    repeat with w in windows
        repeat with t in tabs of w
            set tabTitle to title of t
            set tabURL to URL of t

            if tabTitle contains "{search_term}" or tabURL contains "{search_term}" then
                close t
                return "closed"
            end if
        end repeat
    end repeat

    return "not_found"
end tell
'''

    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=True,
        )

        result_text = result.stdout.strip()

        if result_text == "closed":
            return {
                "success": True,
                "action": "close_chrome_tab",
                "target": search_term,
                "message": f"Chrome tab matching '{search_term}' closed successfully.",
            }

        return {
            "success": False,
            "action": "close_chrome_tab",
            "target": search_term,
            "message": f"No Chrome tab matching '{search_term}' was found.",
        }

    except subprocess.CalledProcessError as error:
        return {
            "success": False,
            "action": "close_chrome_tab",
            "target": search_term,
            "message": error.stderr.strip()
            or "Unable to close Chrome tab.",
        }