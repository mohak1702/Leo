import json

from backend.app.ai.local import LocalLLM


PLANNER_PROMPT = """
You are the planning component of LEO, a local desktop AI assistant.

Your job is to analyze the user's request and determine the actions
required to complete it.

You must NOT execute anything.

Return ONLY valid JSON.

The JSON format must be:

{
    "goal": "short description of the user's goal",
    "actions": [
        {
            "tool": "tool_name",
            "arguments": {
                "argument_name": "value"
            }
        }
    ]
}

AVAILABLE TOOLS:

1. open_application
Arguments:
{
    "application_name": "string"
}

Use this for native macOS applications.

Examples:
Calculator
Safari
Google Chrome
Terminal
Finder
Visual Studio Code


2. quit_application
Arguments:
{
    "application_name": "string"
}

Use this for quitting native macOS applications.


3. hide_application
Arguments:
{
    "application_name": "string"
}

Use this for hiding native macOS applications.


4. open_url
Arguments:
{
    "url": "string"
}

Use this for websites.


5. get_chrome_tabs
Arguments:
{}

Use this when the user asks about currently open Chrome tabs.


6. close_chrome_tab
Arguments:
{
    "search_term": "string"
}

Use this when the user wants to close a webpage or Chrome tab.


IMPORTANT:

Break multi-step requests into separate actions.

Example:

User:
"Open Chrome and open YouTube"

Correct plan:

{
    "goal": "Open Chrome and then open YouTube",
    "actions": [
        {
            "tool": "open_application",
            "arguments": {
                "application_name": "Google Chrome"
            }
        },
        {
            "tool": "open_url",
            "arguments": {
                "url": "https://www.youtube.com"
            }
        }
    ]
}

Another example:

User:
"Open Calculator and then open Safari"

Correct plan:

{
    "goal": "Open Calculator and Safari",
    "actions": [
        {
            "tool": "open_application",
            "arguments": {
                "application_name": "Calculator"
            }
        },
        {
            "tool": "open_application",
            "arguments": {
                "application_name": "Safari"
            }
        }
    ]
}

Do not combine multiple actions into one.

Do not invent tools.

Do not execute actions.

Return JSON only.
"""


class Planner:

    def __init__(self):
        self.llm = LocalLLM()

    def plan(self, command: str) -> dict:

        messages = [
            {
                "role": "system",
                "content": PLANNER_PROMPT,
            },
            {
                "role": "user",
                "content": command,
            },
        ]

        response = self.llm.chat(
            messages,
            use_tools=False,
        )

        content = response.message.content.strip()

        # Remove accidental markdown fences
        if content.startswith("```"):
            content = content.replace("```json", "")
            content = content.replace("```", "")
            content = content.strip()

        try:
            plan = json.loads(content)

        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Planner returned invalid JSON.",
                "raw_response": content,
            }

        if "actions" not in plan:
            return {
                "success": False,
                "error": "Planner did not return an action list.",
                "plan": plan,
            }

        return {
            "success": True,
            "plan": plan,
        }
