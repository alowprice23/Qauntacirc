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

        llm_response = await self.llm_client.complete({"prompt": formatted_prompt})

        if not llm_response.get("content"):
            raise ValueError("LLM failed to provide content.")

        return llm_response["content"]
