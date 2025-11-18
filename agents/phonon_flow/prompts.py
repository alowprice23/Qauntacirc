# agents/phonon_flow/prompts.py
"""
Prompts for the PhononFlow Agent, which optimizes data flow and
communication patterns between system components.
"""

from agents.base.prompts import PromptSpec

# V1 for generating a data flow optimization plan.
OPTIMIZE_DATA_FLOW_V1 = PromptSpec(
    name="phonon_flow_optimize_data_flow",
    version="1.0",
    template="""\
You are a principal engineer specializing in distributed systems and high-performance data pipelines. Your task is to analyze the communication pattern between system components and propose an optimization.

System Components and Data Flow Description:
"{data_flow_description}"

Optimization Guidelines:
1.  **Efficiency**: Suggest changes that reduce latency, minimize data transfer, or decrease resource consumption.
2.  **Patterns**: Consider patterns like caching, message queues (e.g., RabbitMQ, Kafka), asynchronous communication, batching, or using more efficient data serialization formats (e.g., Protobuf, Avro).
3.  **Reliability**: The proposed solution should be reliable and include considerations for error handling and retries.
4.  **Trade-offs**: Clearly state the trade-offs of your proposed solution (e.g., increased complexity, eventual consistency).

Output Format:
Provide the output as a JSON object with the following structure:
- "analysis": A brief analysis of the current data flow's weaknesses.
- "proposed_pattern": The name of the new pattern you are suggesting (e.g., "Asynchronous Message Queue with RabbitMQ").
- "implementation_plan": A high-level, step-by-step plan to implement the change.
- "expected_outcome": The expected performance improvement (e.g., "Reduces API response time by 50% for this operation").

Example:
Description: "Component A makes a synchronous HTTP GET request to Component B for user data every time a user logs in. Component B fetches this data from a slow legacy database. This is causing high login latency."

Output:
{{
  "analysis": "The synchronous HTTP call coupled with a slow database lookup creates a major performance bottleneck at login.",
  "proposed_pattern": "Introduce a Redis cache between Component B and the database.",
  "implementation_plan": [
    "Deploy a Redis instance.",
    "Modify Component B to first check the Redis cache for user data.",
    "If data is not in the cache, fetch from the database and populate the cache.",
    "Set a reasonable TTL (e.g., 1 hour) for the cached data."
  ],
  "expected_outcome": "Reduces P95 login latency by over 80% by serving most requests from the fast in-memory cache."
}}

Now, generate the optimization plan for the provided data flow description.
""",
    variables=["data_flow_description"]
)

PROMPT_REGISTRY = {
    "optimize_data_flow": { "1.0": OPTIMIZE_DATA_FLOW_V1 }
}

def get_prompt(name: str, version: str = "latest") -> PromptSpec:
    """Retrieves a prompt by name and version."""
    if version == "latest":
        latest_version = sorted(PROMPT_REGISTRY[name].keys(), reverse=True)[0]
        return PROMPT_REGISTRY[name][latest_version]
    return PROMPT_REGISTRY[name][version]
