"""
Prompts for the HydroSpread Agent.
"""
from agents.base.prompts import PromptSpec

GENERATE_GROWTH_FORECAST_V1 = PromptSpec(
    name="hydrospread_generate_growth_forecast",
    version="1.0",
    template="""\
You are a project manager with expertise in software project forecasting. Your task is to analyze the following project metrics and provide a growth forecast.

Project Metrics:
- Current number of tasks: {num_tasks}
- Average task complexity (energy): {avg_energy}
- Development viscosity (friction): {viscosity}
- Forecasted code size: {forecasted_size} lines of code

Analysis Guidelines:
1.  **Summarize the Forecast**: State the forecasted code size.
2.  **Explain the Model**: Briefly explain that the forecast is based on a hydrodynamic model that considers the number of tasks, their complexity, and the development friction.
3.  **Provide Recommendations**: Suggest actions to manage the expected growth (e.g., "Consider running the PauliGuard agent to reduce duplication and slow down code growth.").

Output Format:
Provide the output as a JSON object with the following keys: "summary", "explanation", "recommendations".

Now, generate the growth forecast analysis.
""",
    variables=["num_tasks", "avg_energy", "viscosity", "forecasted_size"]
)

PROMPT_REGISTRY = {
    "generate_growth_forecast": {
        "1.0": GENERATE_GROWTH_FORECAST_V1
    }
}

def get_prompt(name: str, version: str = "latest") -> PromptSpec:
    """Retrieves a prompt by name and version."""
    if version == "latest":
        latest_version = sorted(PROMPT_REGISTRY[name].keys(), reverse=True)[0]
        return PROMPT_REGISTRY[name][latest_version]
    return PROMPT_REGISTRY[name][version]
