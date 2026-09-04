import json

from backend.app.ai.local import LocalLLM
from backend.app.agent.tool_registry import build_tool_definitions


class Planner:

    def __init__(self):
        self.llm = LocalLLM()

    def _build_planner_prompt(self) -> str:
        """
        Build the planner prompt dynamically from the registered
        LEO tools.
        """

        tool_definitions = build_tool_definitions()

        tools_text = []

        for tool in tool_definitions:
            function = tool["function"]

            name = function["name"]
            description = function["description"]
            parameters = function["parameters"]

            tools_text.append(
                f"""
TOOL: {name}

DESCRIPTION:
{description}

PARAMETERS:
{json.dumps(parameters, indent=2)}
"""
            )

        available_tools = "\n".join(tools_text)

        return f"""
You are the planning component of LEO
(Local Execution & Orchestration).

Your job is to analyze the user's request and create
a sequence of actions required to complete it.

You must NOT execute anything.

Return ONLY valid JSON.

JSON FORMAT:

{{
    "goal": "short description of the user's goal",
    "actions": [
        {{
            "tool": "tool_name",
            "arguments": {{
                "argument": "value"
            }}
        }}
    ]
}}

AVAILABLE LEO TOOLS:

{available_tools}

IMPORTANT RULES:

1. Only use tools from the AVAILABLE LEO TOOLS list.

2. Never invent a tool.

3. Never execute a tool.

4. Break multi-step requests into separate actions.

5. Preserve the correct order of actions.

6. Use the tool description to determine which tool is
appropriate.

7. Native macOS applications should use application tools.

8. Websites, webpages, browser tabs, and web services
should use browser tools.

9. If the user specifies a browser, the website must be
opened inside that browser.

Example:

User:
"Open Safari and open YouTube"

Plan:

{{
    "goal": "Open Safari and then open YouTube in Safari",
    "actions": [
        {{
            "tool": "open_application",
            "arguments": {{
                "application_name": "Safari"
            }}
        }},
        {{
            "tool": "open_url_in_browser",
            "arguments": {{
                "url": "https://www.youtube.com",
                "browser": "Safari"
            }}
        }}
    ]
}}

10. If the user specifies Google Chrome or Chrome,
use "Google Chrome" as the browser name.

Example:

User:
"Open Chrome and open GitHub"

Plan:

{{
    "goal": "Open Google Chrome and then open GitHub in Google Chrome",
    "actions": [
        {{
            "tool": "open_application",
            "arguments": {{
                "application_name": "Google Chrome"
            }}
        }},
        {{
            "tool": "open_url_in_browser",
            "arguments": {{
                "url": "https://github.com",
                "browser": "Google Chrome"
            }}
        }}
    ]
}}

11. If the user does not specify a browser,
use "open_url" to open the website in the default browser.

Example:

User:
"Open YouTube"

Plan:

{{
    "goal": "Open YouTube",
    "actions": [
        {{
            "tool": "open_url",
            "arguments": {{
                "url": "https://www.youtube.com"
            }}
        }}
    ]
}}

12. If the user asks for multiple actions,
include every required action in the actions array.

13. Do not combine multiple actions into one action.

14. Preserve dependencies between actions.

For example, if the user says:
"Open Safari and then open YouTube in Safari"

the Safari application must be opened before
the YouTube URL is opened.

15. Only provide arguments required by the selected tool.

16. Do not add explanations outside the JSON.

17. Return valid JSON only.
"""

    def plan(self, command: str) -> dict:
        """
        Convert a natural-language user command into
        a structured execution plan.
        """

        command = command.strip()

        if not command:
            return {
                "success": False,
                "error": "Command cannot be empty.",
            }

        planner_prompt = self._build_planner_prompt()

        messages = [
            {
                "role": "system",
                "content": planner_prompt,
            },
            {
                "role": "user",
                "content": command,
            },
        ]

        try:
            response = self.llm.chat(
                messages,
                use_tools=False,
            )

            content = response.message.content.strip()

        except Exception as error:
            return {
                "success": False,
                "error": f"Planner failed: {error}",
            }

        # Remove accidental Markdown code fences.
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

        if not isinstance(plan, dict):
            return {
                "success": False,
                "error": "Planner response must be a JSON object.",
                "raw_response": content,
            }

        if "goal" not in plan:
            return {
                "success": False,
                "error": "Planner did not return a goal.",
                "plan": plan,
            }

        if "actions" not in plan:
            return {
                "success": False,
                "error": "Planner did not return an action list.",
                "plan": plan,
            }

        if not isinstance(plan["actions"], list):
            return {
                "success": False,
                "error": "Planner actions must be a list.",
                "plan": plan,
            }

        return {
            "success": True,
            "plan": plan,
        }