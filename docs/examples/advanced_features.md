# Example: Advanced Features

This document showcases some of the advanced features of the QuantaCirc system, including LLM integration and inter-agent communication via the messaging bus.

## 1. Using an LLM in an Agent

Agents can leverage Large Language Models (LLMs) to perform complex reasoning tasks. Here is an example of an agent that uses an `OpenAIClient` to generate a summary for a file.

```python
# agents/summarization_agent.py
from agents.base.agent import BaseAgent
from core.types import State, Transition, Operation
from llm.openai_client import OpenAIClient

class SummarizationAgent(BaseAgent):
    def __init__(self, state):
        super().__init__(state)
        self.llm_client = OpenAIClient(model="gpt-4-turbo")

    def propose_transition(self, state: State) -> Transition:
        operations = []
        for file_info in state.get("files", []):
            # Check if the file has content but no summary
            if file_info.get("content") and not file_info.get("summary"):

                # Use the LLM to generate a summary
                prompt = f"Summarize the following text: {file_info['content']}"
                summary = self.llm_client.get_completion(prompt)

                op = Operation(
                    op_type="ADD_SUMMARY",
                    path=file_info["path"],
                    payload={"summary": summary}
                )
                operations.append(op)

        return Transition(operations=operations)
```

## 2. Publishing Events to the Message Bus

Agents can communicate with external systems or other agents by publishing events to the message bus.

```python
# agents/event_publisher_agent.py
from agents.base.agent import BaseAgent
from core.types import State, Transition
from messaging.publisher import Publisher

class EventPublisherAgent(BaseAgent):
    def __init__(self, state):
        super().__init__(state)
        # Assume publisher is initialized and connected
        self.publisher = Publisher()

    def propose_transition(self, state: State) -> Transition:
        # After a successful operation, publish an event
        if state.get("last_operation_successful"):
            event_message = {
                "event_type": "file_processed",
                "file_path": state.get("last_processed_file")
            }
            self.publisher.publish("agent.events.processed", event_message)

        return Transition(operations=[])
```

## 3. Advanced Project Configuration

The `qc_config.yml` file can be used to configure complex interactions between multiple agents and fine-tune the engine's performance.

```yaml
# qc_config.yml
project_name: "AdvancedProject"

agents:
  - name: "MetadataAgent"
    enabled: true
  - name: "SummarizationAgent"
    enabled: true
    # Agent-specific config
    config:
      model: "gpt-4-turbo"
  - name: "EventPublisherAgent"
    enabled: true

# Use a different annealing schedule
engine_params:
  annealing_schedule: "exponential"
  initial_temp: 100.0
  final_temp: 0.1
```

This configuration sets up a pipeline where one agent adds metadata, another generates summaries using an LLM, and a third publishes events upon completion. This demonstrates the power of composing multiple specialized agents to solve complex problems.
