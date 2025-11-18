# agents/hydro_spread/prompts.py
"""
Prompts for the HydroSpread Agent, which models and forecasts the
evolution of system complexity.
"""

from agents.base.prompts import PromptSpec

# V1 for forecasting complexity growth.
FORECAST_COMPLEXITY_V1 = PromptSpec(
    name="hydro_spread_forecast_complexity",
    version="1.0",
    template="""\
You are a quantitative analyst specializing in software evolution and complexity theory. Your task is to analyze historical system metrics and forecast future growth and potential scaling challenges.

Historical Data Summary:
"{historical_data_summary}"

Forecasting Guidelines:
1.  **Identify Trends**: Analyze the provided data to identify key trends (e.g., linear growth in dependencies, exponential growth in code size).
2.  **Extrapolate**: Provide a qualitative forecast for the next development cycle (e.g., "Complexity is expected to increase by approximately 15%").
3.  **Identify Scaling Risks**: Based on the trends, identify the top 1-2 risks related to system scaling (e.g., "The rapid growth in inter-module dependencies suggests a risk of the system becoming a 'big ball of mud'").
4.  **Suggest Proactive Measures**: Recommend one high-level proactive measure to mitigate the identified risks (e.g., "Consider introducing stricter modular boundaries or a formal API gateway").

Output Format:
Provide the output as a JSON object with the following structure:
- "trend_analysis": A short description of the observed trends.
- "complexity_forecast": A qualitative forecast of future complexity.
- "scaling_risks": A list of identified scaling risks.
- "proactive_suggestions": A list of suggested measures.

Example:
... (Example is omitted for brevity, the structure is defined above)

Now, provide the complexity forecast based on the provided data.
""",
    variables=["historical_data_summary"]
)

PROMPT_REGISTRY = {
    "forecast_complexity": { "1.0": FORECAST_COMPLEXITY_V1 }
}

def get_prompt(name: str, version: str = "latest") -> PromptSpec:
    """Retrieves a prompt by name and version."""
    if version == "latest":
        latest_version = sorted(PROMPT_REGISTRY[name].keys(), reverse=True)[0]
        return PROMPT_REGISTRY[name][latest_version]
    return PROMPT_REGISTRY[name][version]
