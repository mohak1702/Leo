from backend.app.agent.tool_registry import get_tool
from backend.app.ai.local import LocalLLM, SYSTEM_PROMPT


class Agent:
    """
    Core execution engine for LEO.

    The agent can reason, execute tools, observe their results,
    and retry with another tool when necessary.
    """

    MAX_TOOL_STEPS = 3

    def execute(self, tool_name: str, **arguments) -> dict:
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

    def run(self, command: str) -> dict:
        llm = LocalLLM()

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": command,
            },
        ]

        tool_history = []

        for step in range(self.MAX_TOOL_STEPS):

            response = llm.chat(messages)
            message = response.message

            # No tool requested → normal/final response
            if not message.tool_calls:
                return {
                    "success": True,
                    "command": command,
                    "action": (
                        "conversation"
                        if not tool_history
                        else "tool_execution"
                    ),
                    "response": message.content,
                    "tool_history": tool_history,
                }

            # Prevent obvious conversational questions
            # from accidentally triggering computer tools.
            if (
                not tool_history
                and self._looks_like_conversation(command)
            ):
                messages = [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT + """

The user is asking for information or conversation.
Do not call a computer tool.
Answer directly.
""",
                    },
                    {
                        "role": "user",
                        "content": command,
                    },
                ]

                conversation_response = llm.chat(messages)

                return {
                    "success": True,
                    "command": command,
                    "action": "conversation",
                    "response": conversation_response.message.content,
                }

            tool_call = message.tool_calls[0]

            tool_name = tool_call.function.name
            arguments = dict(tool_call.function.arguments)

            execution = self.execute(
                tool_name,
                **arguments,
            )

            tool_history.append(
                {
                    "tool": tool_name,
                    "arguments": arguments,
                    "execution": execution,
                }
            )

            # Preserve assistant tool call
            messages.append(message)

            # Give actual result back to the model
            messages.append(
                {
                    "role": "tool",
                    "tool_name": tool_name,
                    "content": str(execution),
                }
            )

            # Successful action:
            # allow LLM one more turn to describe what happened.
            if execution["success"]:
                final_response = llm.chat(messages)

                # If it unexpectedly requests another tool,
                # continue the agent loop.
                if final_response.message.tool_calls:
                    messages.append(final_response.message)
                    continue

                return {
                    "success": True,
                    "command": command,
                    "action": "tool_execution",
                    "tool": tool_name,
                    "arguments": arguments,
                    "execution": execution,
                    "tool_history": tool_history,
                    "response": final_response.message.content,
                }

            # Tool failed.
            # Tell LLM to reconsider instead of pretending success.
            messages.append(
                {
                    "role": "system",
                    "content": (
                        "The previous tool failed. Reconsider the user's "
                        "original request. If another available tool can "
                        "perform the request, use it. Do not claim success "
                        "unless a tool succeeds."
                    ),
                }
            )

        return {
            "success": False,
            "command": command,
            "action": "failed",
            "tool_history": tool_history,
            "response": (
                "I couldn't complete the request after trying "
                "the available tools."
            ),
        }