# agents/fluctua_test/prompts.py
"""
Prompts for the FluctuaTest Agent, which designs and executes chaos
engineering experiments to test system resilience.
"""

from agents.base.prompts import PromptSpec

# V1 for generating a chaos engineering experiment plan.
GENERATE_CHAOS_TEST_V1 = PromptSpec(
    name="fluctua_test_generate_chaos_test",
    version="1.0",
    template="""\
You are a seasoned chaos engineer and systems reliability expert. Your task is to design a chaos engineering experiment for the given system architecture to test its resilience against turbulent conditions.

System Architecture Description:
"{architecture_description}"

Chaos Experiment Design Rules:
1.  **Start with a Hypothesis**: Formulate a clear, measurable hypothesis about how the system will behave during a failure. The system should exhibit resilience, not just fail.
2.  **Inject a Realistic Fault**: Propose a specific, realistic fault to inject. Examples: high network latency, CPU overload on a specific service, DNS failure, database connection pool exhaustion.
3.  **Define Steady State**: Describe the normal operating behavior of the system (the "steady state").
4.  **Identify Metrics**: List the key metrics to monitor during the experiment to observe deviations from the steady state (e.g., error rates, latency percentiles, queue depths).
5.  **Define Success Criteria**: The success of the experiment is not "nothing broke," but "our hypothesis was confirmed." State what a successful outcome looks like.

Output Format:
Provide the output as a JSON object with the following structure:
- "experiment_name": A descriptive name for the chaos experiment.
- "hypothesis": The hypothesis being tested.
- "fault_to_inject": A clear description of the fault injection method.
- "metrics_to_monitor": A list of key performance indicators.
- "success_criteria": A description of the expected resilient behavior.

Example:
Architecture: "A web application with a load balancer, 3 API servers, and a PostgreSQL database. A Redis cache is used for session data."
Output:
{{
  "experiment_name": "API Resilience to Database Failure",
  "hypothesis": "If the PostgreSQL database becomes unavailable, the API servers will detect the failure, return a '503 Service Unavailable' error for database-dependent requests, but continue to serve requests that only rely on the Redis cache.",
  "fault_to_inject": "Add firewall rules to block all TCP traffic from the API servers to the PostgreSQL database on port 5432 for 5 minutes.",
  "metrics_to_monitor": ["API server P99 latency", "API server error rate (5xx)", "Database connection errors"],
  "success_criteria": "The system is considered resilient if the overall API error rate rises but does not reach 100%, and requests for cached data succeed, confirming the system's partial degradation."
}}

Now, design a chaos experiment for the provided architecture.
""",
    variables=["architecture_description"]
)

PROMPT_REGISTRY = {
    "generate_chaos_test": { "1.0": GENERATE_CHAOS_TEST_V1 }
}

def get_prompt(name: str, version: str = "latest") -> PromptSpec:
    """Retrieves a prompt by name and version."""
    if version == "latest":
        latest_version = sorted(PROMPT_REGISTRY[name].keys(), reverse=True)[0]
        return PROMPT_REGISTRY[name][latest_version]
    return PROMPT_REGISTRY[name][version]
