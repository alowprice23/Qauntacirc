import asyncio
import logging
from typing import List, Dict, Any

from agents.base.agent import QuantumAgent
from core.config_loader import load_config
from core.types import QuantaCircConfig, AgentTask, AgentResult, Status
from .prompts import get_prompt
from .ops import extract_python_code, validate_python_syntax, CodeGenerationError

log = logging.getLogger(__name__)

class SchrodingerDevAgent(QuantumAgent):
    """
    An agent that generates code based on quantized tasks.
    """
    def __init__(self, config: QuantaCircConfig):
        super().__init__(name="SchrodingerDev", config=config)

    @property
    def capabilities(self) -> List[str]:
        return ["code_generation", "api_implementation"]

    async def process_task(self, task: AgentTask) -> AgentResult:
        log.info(f"SchrodingerDev received task: {task.payload}")
        try:
            task_description = task.payload.get("description", "")
            if not task_description:
                raise ValueError("Task payload must contain a 'description'.")

            # 1. Get and format the prompt
            prompt_spec = get_prompt("generate_code", version="latest")
            prompt = prompt_spec.format(
                task_description=task_description,
                verification_criteria=task.payload.get("verification_criteria", "None"),
                template_name=task.payload.get("template_name", "default")
            )

            # 2. Call the LLM to generate code, with fallback
            # Adjust temperature for deterministic code generation
            log.info("Generating code with LLM...")
            llm_response = await self.llm_generate_with_fallback(prompt, temperature=0.0)

            # 3. Extract and validate the code
            generated_code = extract_python_code(llm_response)
            validate_python_syntax(generated_code)
            log.info("Successfully generated and validated code.")

            # 4. Create result
            result_payload = {
                "message": "Code generated successfully.",
                "generated_code": generated_code,
                "files_created": [f"src/generated/{task.id}.py"],
            }
            return AgentResult(
                task_id=task.id, agent_name=self.name, action_taken=True,
                result=result_payload, status=Status.SUCCESS
            )
        except (CodeGenerationError, ValueError) as e:
            log.error(f"Error during code generation: {e}")
            return AgentResult(
                task_id=task.id, agent_name=self.name, action_taken=False,
                error=str(e), status=Status.FAILED
            )
        except Exception as e:
            log.error(f"An unexpected error occurred in SchrodingerDevAgent: {e}", exc_info=True)
            return AgentResult(
                task_id=task.id, agent_name=self.name, action_taken=False,
                error=f"An unexpected error occurred: {e}", status=Status.FAILED
            )


async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    config = load_config()
    agent = SchrodingerDevAgent(config)
    try:
        await agent.start()
        log.info("SchrodingerDev Agent is running. Press Ctrl+C to stop.")
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        log.info("SchrodingerDev Agent is shutting down.")
    finally:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())