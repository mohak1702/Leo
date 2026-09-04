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

8. Websites and browser content should use browser tools.

9. If the user asks for multiple actions, include every
required action in the actions array.

10. Do not combine multiple actions into one action.

11. Return valid JSON only.

Example:

User:
"Open Chrome and open YouTube"

Plan:

{{
    "goal": "Open Chrome and then open YouTube",
    "actions": [
        {{
            "tool": "open_application",
            "arguments": {{
                "application_name": "Google Chrome"
            }}
        }},
        {{
            "tool": "open_url",
            "arguments": {{
                "url": "https://www.youtube.com"
            }}
        }}
    ]
}}
"""

    def plan(self, command: str) -> dict:

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

        response = self.llm.chat(
            messages,
            use_tools=False,
        )

        content = response.message.content.strip()

        # Remove accidental markdown code fences
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