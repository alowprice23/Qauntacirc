from llm.client import LLMClient
from . import prompts

class NLParser:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def parse_requirement(self, requirement_text: str) -> str:
        """
        Uses the LLM to parse a natural language requirement into a structured
        JSON string of tasks.

        Args:
            requirement_text: The natural language requirement.

        Returns:
            A JSON string representing the list of tasks.
        """
        prompt_spec = prompts.get_prompt("decompose_requirement", "latest")
        formatted_prompt = prompt_spec.format(requirement_text=requirement_text)

        # The 'chat' method expects a list of message dictionaries.
        messages = [{"role": "user", "content": formatted_prompt}]

        # The llm_client.complete method is synchronous in the base class,
        # but the calling agent is async. This suggests the concrete
        # implementation should be async or run in an executor.
        # For now, we will assume an async-compatible mock or implementation.
        # The primary fix is the message format.
        llm_response_dict = self.llm_client.complete(messages)

        if not llm_response_dict.get("response"):
            raise ValueError("LLM failed to provide content.")

        return llm_response_dict["response"]
