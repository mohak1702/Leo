from backend.app.agent.tool_registry import get_tool
from backend.app.ai.local import LocalLLM, SYSTEM_PROMPT
from backend.app.agent.planner import Planner


class Agent:

    def __init__(self):
        self.llm = LocalLLM()
        self.planner = Planner()

    def execute(self, tool_name: str, **arguments) -> dict:
        """
        Execute one registered LEO tool.
        """

        tool = get_tool(tool_name)

        if tool is None:
            return {
                "success": False,
                "tool": tool_name,
                "error": f"Tool '{tool_name}' is not registered.",
            }

        try:
            result = tool(**arguments)

            return {
                "success": result.get("success", False),
                "tool": tool_name,
                "result": result,
            }

        except Exception as error:
            return {
                "success": False,
                "tool": tool_name,
                "error": str(error),
            }

    def _looks_like_conversation(self, command: str) -> bool:
        """
        Detect obvious conversation/question requests.

        These requests should not enter the computer execution
        pipeline.
        """

        text = command.strip().lower()

        conversation_starters = (
            "what ",
            "who ",
            "why ",
            "how ",
            "when ",
            "where ",
            "which ",
            "tell me ",
            "explain ",
            "can you explain ",
            "are you ",
            "do you ",
            "hello",
            "hi ",
            "hey ",
        )

        return text.startswith(conversation_starters)

    def _clean_response(self, response: str) -> str:
        """
        Clean the final LLM response.
        """

        if not response:
            return "I'm here. How can I help?"

        response = response.strip()

        if response.startswith("assistant"):
            response = response[len("assistant"):].strip()

        return response

    def _conversation(self, command: str) -> dict:
        """
        Handle normal conversation without tools.
        """

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
                + """

The current request is conversation or a question.

Do not perform any computer action.

Answer the user directly and naturally.
""",
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

        return {
            "success": True,
            "command": command,
            "action": "conversation",
            "response": self._clean_response(
                response.message.content
            ),
        }

    def _create_final_response(
        self,
        command: str,
        execution_results: list,
    ) -> str:
        """
        Ask the local model to summarize what happened.
        """

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
                + """

You are now generating the final response after executing
one or more computer actions.

Use ONLY the execution results provided.

Do not invent actions or results.

If an action failed, tell the user honestly.

Keep the response short and natural.
""",
            },
            {
                "role": "user",
                "content": command,
            },
            {
                "role": "user",
                "content": (
                    "Execution results:\n"
                    + str(execution_results)
                ),
            },
        ]

        response = self.llm.chat(
            messages,
            use_tools=False,
        )

        return self._clean_response(
            response.message.content
        )

    def run(self, command: str) -> dict:
        """
        Main LEO agent pipeline.

        Conversation:
            User → LLM → Response

        Action:
            User → Planner → Executor → Results → LLM → Response
        """

        command = command.strip()

        if not command:
            return {
                "success": False,
                "action": "invalid",
                "response": "Please give me a command.",
            }

        # -----------------------------------------
        # CONVERSATION
        # -----------------------------------------

        if self._looks_like_conversation(command):
            return self._conversation(command)

        # -----------------------------------------
        # PLANNING
        # -----------------------------------------

        planning = self.planner.plan(command)

        if not planning["success"]:
            return {
                "success": False,
                "command": command,
                "action": "planning_failed",
                "response": (
                    "I couldn't create a plan for that request."
                ),
                "planner": planning,
            }

        plan = planning["plan"]

        actions = plan.get("actions", [])

        if not actions:
            return {
                "success": False,
                "command": command,
                "action": "no_actions",
                "response": (
                    "I couldn't find an action required "
                    "for that request."
                ),
                "plan": plan,
            }

        # -----------------------------------------
        # EXECUTION
        # -----------------------------------------

        execution_results = []

        for index, action in enumerate(actions, start=1):

            tool_name = action.get("tool")

            arguments = action.get(
                "arguments",
                {},
            )

            result = self.execute(
                tool_name,
                **arguments,
            )

            execution_results.append(
                {
                    "step": index,
                    "tool": tool_name,
                    "arguments": arguments,
                    "execution": result,
                }
            )

            # Stop if an action fails.
            #
            # We do not blindly continue because later actions
            # may depend on the failed action.
            if not result["success"]:
                break

        # -----------------------------------------
        # FINAL RESPONSE
        # -----------------------------------------

        final_response = self._create_final_response(
            command,
            execution_results,
        )

        return {
            "success": all(
                item["execution"]["success"]
                for item in execution_results
            ),
            "command": command,
            "action": "planned_execution",
            "response": final_response,
            "plan": plan,
            "tool_history": execution_results,
        }