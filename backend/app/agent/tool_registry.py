from backend.app.tools.computer import (
    open_application,
    quit_application,
    hide_application,
    take_screenshot,
)
from backend.app.tools.browser import (
    open_url,
    open_url_in_browser,
    get_chrome_tabs,
    close_chrome_tab,
)


TOOLS = {
    "open_application": {
        "function": open_application,
        "description": "Open a macOS application by its name.",
        "parameters": {
            "type": "object",
            "properties": {
                "application_name": {
                    "type": "string",
                    "description": "The name of the macOS application to open.",
                }
            },
            "required": ["application_name"],
        },
    },

    "quit_application": {
        "function": quit_application,
        "description": (
            "Quit a running native macOS application such as Safari, "
            "Calculator, Terminal, Finder, or Google Chrome. "
            "Do not use this for websites or browser tabs."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "application_name": {
                    "type": "string",
                    "description": "The name of the macOS application to quit.",
                }
            },
            "required": ["application_name"],
        },
    },

    "hide_application": {
        "function": hide_application,
        "description": "Hide a running macOS application.",
        "parameters": {
            "type": "object",
            "properties": {
                "application_name": {
                    "type": "string",
                    "description": "The name of the macOS application to hide.",
                }
            },
            "required": ["application_name"],
        },
    },

    "open_url": {
        "function": open_url,
        "description": "Open a website URL in the user's default browser.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The complete URL to open.",
                }
            },
            "required": ["url"],
        },
    },

    "get_chrome_tabs": {
        "function": get_chrome_tabs,
        "description": "Get the currently open tabs in Google Chrome.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },

        "open_url_in_browser": {
        "function": open_url_in_browser,
        "description": (
            "Open a website URL inside a specific browser such as "
            "Safari or Google Chrome."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The complete URL to open.",
                },
                "browser": {
                    "type": "string",
                    "description": (
                        "The browser to use, such as Safari "
                        "or Google Chrome."
                    ),
                },
            },
            "required": ["url", "browser"],
        },
    },

        "take_screenshot": {
        "function": take_screenshot,
        "description": (
            "Capture the current macOS screen as an image. "
            "Use this when LEO needs to observe the current "
            "visual state of the computer."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },

    "close_chrome_tab": {
        "function": close_chrome_tab,
        "description": (
            "Close an open Google Chrome browser tab by matching "
            "its title or URL. Use this when the user wants to "
            "close a website, webpage, or web service currently "
            "open in Chrome."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "search_term": {
                    "type": "string",
                    "description": (
                        "The word or phrase to search for in Chrome "
                        "tab titles or URLs."
                    ),
                }
            },
            "required": ["search_term"],
        },
    },
}


def get_tool(tool_name: str):
    """Return the executable function for a registered tool."""

    tool = TOOLS.get(tool_name)

    if tool is None:
        return None

    return tool["function"]


def list_tools() -> list:
    """Return all registered tool names."""

    return list(TOOLS.keys())


def build_tool_definitions() -> list:
    """
    Convert the tool registry into Ollama-compatible
    function-calling definitions.
    """

    definitions = []

    for name, data in TOOLS.items():
        definitions.append(
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": data["description"],
                    "parameters": data["parameters"],
                },
            }
        )

    return definitions